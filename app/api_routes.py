from flask import Blueprint, jsonify, request
from app.logic.consumidor import Consumidor
from app.logic.encomendas import GestorEncomendas, Encomenda
from app.logic.impacto import exibir_resumo_impacto
from app.utils.data_loader import carregar_produtos, carregar_supermercados

api = Blueprint("api", __name__)

produtos = carregar_produtos()
supermercados = carregar_supermercados()
gestor = GestorEncomendas()


@api.route("/", methods=["GET"])
def home():
    return (
        """
        <html lang=\"pt-br\">
        <head>
            <meta charset=\"UTF-8\">
            <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
            <title>AZURE API</title>
            <link 
                href=\"https://cdn.jsdelivr.net/npm/tailwindcss@2.0.0/dist/tailwind.min.css\" 
                rel=\"stylesheet\">
            <link 
                href=\"https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.1/css/all.min.css\" 
                rel=\"stylesheet\">
            <style>
                .custom-gradient {
                    background: linear-gradient(135deg, #6EE7B7, #3B82F6);
                }
                .hover\\:scale-up:hover {
                    transform: scale(1.05);
                }
                .fade-in {
                    animation: fadeIn 1s ease-in-out;
                }
                @keyframes fadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }
            </style>
        </head>
        <body class=\"bg-gray-50 font-sans text-gray-900\">
            <header 
                class=\"bg-gradient-to-r from-green-400 to-blue-500 text-white \
                py-12 shadow-lg fade-in\">
                <div class=\"container mx-auto text-center\">
                    <h1 class=\"text-4xl font-bold mb-4\">🚀 AZURE API</h1>
                    <p class=\"text-lg mb-6\">
                        Bem-vindo à nossa API! Interaja com os endpoints abaixo:
                    </p>
                </div>
            </header>
            <div class=\"container mx-auto mt-10 px-4\">
                <div 
                    class=\"grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 text-center\">
                    <a href=\"/api/produtos\"
                       class=\"bg-white p-6 rounded-lg shadow-xl hover:scale-up \
                       transition-all duration-300\">
                        <i class=\"fas fa-cube text-4xl text-blue-500 mb-4\"></i>
                        <h2 class=\"text-xl font-semibold text-blue-500\">/api/produtos</h2>
                        <p class=\"text-gray-600 mt-2\">
                            Lista de todos os produtos disponíveis na API.
                        </p>
                    </a>
                    <a href=\"/api/supermercados\"
                       class=\"bg-white p-6 rounded-lg shadow-xl hover:scale-up \
                       transition-all duration-300\">
                        <i class=\"fas fa-shopping-cart text-4xl text-green-500 mb-4\"></i>
                        <h2 class=\"text-xl font-semibold text-blue-500\">/api/supermercados</h2>
                        <p class=\"text-gray-600 mt-2\">
                            Descubra todos os supermercados cadastrados na API.
                        </p>
                    </a>
                    <a href=\"/api/impacto\"
                       class=\"bg-white p-6 rounded-lg shadow-xl hover:scale-up \
                       transition-all duration-300\">
                        <i class=\"fas fa-leaf text-4xl text-green-500 mb-4\"></i>
                        <h2 class=\"text-xl font-semibold text-blue-500\">/api/impacto</h2>
                        <p class=\"text-gray-600 mt-2\">
                            Visualize o impacto ambiental das encomendas.
                        </p>
                    </a>
                </div>
            </div>
            <footer class=\"bg-gray-200 py-8 mt-12\">
                <div class=\"container mx-auto text-center\">
                    <p class=\"text-sm text-gray-600\">
                        Para realizar uma encomenda, envie um
                        <a href=\"#\" class=\"text-blue-500 hover:underline\">
                            POST para /api/encomendas
                        </a>
                        com JSON.
                    </p>
                </div>
            </footer>
            <script 
                src=\"https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.1/js/all.min.js\">
            </script>
        </body>
        </html>
        """
    )


@api.route("/api/produtos", methods=["GET"])
def get_produtos():
    lista = [p.to_dict() for p in produtos]
    return jsonify({"success": True, "data": lista})


@api.route("/api/supermercados", methods=["GET"])
def get_supermercados():
    lista = [s.to_dict() for s in supermercados.values()]
    return jsonify({"success": True, "data": lista})


@api.route("/api/encomendas", methods=["POST"])
def criar_encomenda():
    data = request.get_json()
    try:
        supermercado_nome = data["supermercado"]
        produtos_encomendados = data["produtos"]
        supermercado = supermercados.get(supermercado_nome)

        if not supermercado:
            return jsonify({
                "success": False,
                "error": "Supermercado não encontrado"
            }), 404

        consumidor = Consumidor("Utilizador API")
        produtos_selecionados = []

        for item in produtos_encomendados:
            nome_produto = item["nome"]
            quantidade = int(item.get("quantidade", 1))
            produto = next(
                (p for p in produtos if p.nome == nome_produto), None
            )
            if produto:
                produtos_selecionados.extend([produto] * quantidade)

        encomenda = Encomenda(
            consumidor,
            supermercado,
            produtos_selecionados
        )
        gestor.registar_encomenda(encomenda)

        frutas_dict = {}
        for fruta in encomenda.frutas:
            frutas_dict[fruta] = frutas_dict.get(fruta, 0) + 1

        impacto = supermercado.calcular_impacto(frutas_dict)

        return jsonify({
            "success": True,
            "message": "Encomenda criada com sucesso",
            "impacto": {
                supermercado.nome: impacto
            }
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@api.route("/api/impacto", methods=["GET"])
def get_impacto():
    impactos_mercados = {}

    for encomenda in gestor.encomendas:
        nome_mercado = encomenda.supermercado.nome
        if nome_mercado not in impactos_mercados:
            impactos_mercados[nome_mercado] = {}

        for fruta in encomenda.frutas:
            impactos_mercados[nome_mercado][fruta] = (
                impactos_mercados[nome_mercado].get(fruta, 0) + 1
            )

    if not impactos_mercados:
        return jsonify({
            "success": False,
            "error": "Nenhuma encomenda registada"
        }), 400

    resultados = {}
    for nome, frutas_dict in impactos_mercados.items():
        supermercado = supermercados[nome]
        impacto = supermercado.calcular_impacto(frutas_dict)
        resultados[nome] = impacto

    resumo = exibir_resumo_impacto(resultados)
    return jsonify({"success": True, "data": resumo})
