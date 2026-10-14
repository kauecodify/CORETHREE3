import React from 'react';

const ProductGrid = ({ products }) => {
  return (
    <div className="space-y-lg">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-md">
        {products.map(product => (
          <div key={product.id} className="card animate-fade-in">
            <div className="card-header">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="card-title">{product.name}</h3>
                  <span className="text-sm text-gray-500">{product.id}</span>
                </div>
                <span className={`badge badge-${product.status === 'TRL 8' ? 'success' : 'info'}`}>
                  {product.status}
                </span>
              </div>
            </div>
            <div className="card-body">
              <p className="text-gray-600 mb-md">{product.description}</p>
              
              <div className="mb-md">
                <div className="text-sm text-gray-500 mb-xs">Funcionalidades</div>
                <ul className="text-sm text-gray-600 space-y-xs">
                  {product.features.map((feature, index) => (
                    <li key={index} className="flex items-center gap-xs">
                      <span className="text-primary">-</span>
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="flex justify-end">
                <button className="btn btn-primary btn-sm">
                  Acessar Documentacao
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Product Comparison Table */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Comparacao de Produtos</h2>
        </div>
        <div className="card-body">
          <div className="overflow-x-auto">
            <table className="table">
              <thead>
                <tr>
                  <th>Produto</th>
                  <th>Descricao</th>
                  <th>Status TRL</th>
                  <th>Funcionalidades Principais</th>
                  <th>Integracao com Kiro</th>
                </tr>
              </thead>
              <tbody>
                {products.map(product => (
                  <tr key={product.id}>
                    <td className="font-medium text-gray-900">{product.name}</td>
                    <td className="text-gray-600">{product.description}</td>
                    <td>
                      <span className={`badge badge-${product.status === 'TRL 8' ? 'success' : 'info'}`}>
                        {product.status}
                      </span>
                    </td>
                    <td>
                      <ul className="text-sm text-gray-600 space-y-xs">
                        {product.features.slice(0, 2).map((feature, index) => (
                          <li key={index}>- {feature}</li>
                        ))}
                        {product.features.length > 2 && (
                          <li className="text-gray-400">+{product.features.length - 2} mais</li>
                        )}
                      </ul>
                    </td>
                    <td className="text-center">
                      <span className="text-success">Sim</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Architecture Overview */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Arquitetura do CORETHREE3</h2>
        </div>
        <div className="card-body">
          <div className="space-y-md">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-sm">Integracao com Kiro (AWS AI Agent)</h3>
              <p className="text-gray-600 mb-md">
                O CORETHREE3 utiliza o Kiro para desenvolvimento acelerado, otimizacao de operacoes e integracao continua.
              </p>
              <ul className="text-sm text-gray-600 space-y-xs mb-md">
                <li>- Geracao automatica de codigo e testes</li>
                <li>- Analise inteligente de logs e deteccao de anomalias</li>
                <li>- Validacao automatica de APIs e integracao com sistemas legados</li>
                <li>- Otimizacao de modelos de ML e processamento de dados</li>
              </ul>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-sm">Sensores IoT</h3>
              <p className="text-gray-600 mb-md">
                Sensores de baixo custo com alta precisao para monitoramento industrial.
              </p>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-sm text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">Vibracao:</span>
                  <span className="font-medium">R$ 75 - +/-0.1%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Temperatura:</span>
                  <span className="font-medium">R$ 50 - +/-0.5C</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Pressao:</span>
                  <span className="font-medium">R$ 60 - +/-0.2%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Corrente:</span>
                  <span className="font-medium">R$ 80 - +/-0.5%</span>
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-sm">Barreiras Competitivas (Moat)</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-sm">
                <div className="alert alert-info text-sm">
                  <div className="font-medium mb-xs">Modelos de ML Proprietarios</div>
                  <div>Treinados com dados exclusivos de clientes</div>
                </div>
                <div className="alert alert-info text-sm">
                  <div className="font-medium mb-xs">Sensores de Baixo Custo</div>
                  <div>70% mais baratos que concorrentes</div>
                </div>
                <div className="alert alert-info text-sm">
                  <div className="font-medium mb-xs">Integracao Nativa com Kiro</div>
                  <div>Desenvolvimento acelerado e manutencao inteligente</div>
                </div>
                <div className="alert alert-info text-sm">
                  <div className="font-medium mb-xs">Patente Pendente</div>
                  <div>Sistema de Manutencao Preditiva com Sensores</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductGrid;
