import React, { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import SensorDashboard from '../components/SensorDashboard';
import ProductGrid from '../components/ProductGrid';
import StatsOverview from '../components/StatsOverview';

const HomePage = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [sensorData, setSensorData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Simulacao de dados de sensores
  useEffect(() => {
    const fetchSensorData = async () => {
      // Dados mockados - em producao, viria da API
      const mockData = {
        machines: [
          {
            id: 'MACHINE_001',
            name: 'Torno CNC #1',
            status: 'operational',
            sensors: [
              { type: 'vibration', value: 0.3, unit: 'g', status: 'normal', threshold: 0.5 },
              { type: 'temperature', value: 65.2, unit: '°C', status: 'normal', threshold: 70 },
              { type: 'current', value: 12.5, unit: 'A', status: 'normal', threshold: 15 }
            ],
            healthScore: 92,
            lastMaintenance: '2026-10-01',
            nextMaintenance: '2026-11-15',
            prediction: 'Normal operation for next 30 days'
          },
          {
            id: 'MACHINE_002',
            name: 'Injetora #2',
            status: 'warning',
            sensors: [
              { type: 'vibration', value: 0.6, unit: 'g', status: 'warning', threshold: 0.5 },
              { type: 'temperature', value: 78.1, unit: '°C', status: 'warning', threshold: 70 },
              { type: 'pressure', value: 45.3, unit: 'bar', status: 'normal', threshold: 50 }
            ],
            healthScore: 75,
            lastMaintenance: '2026-09-15',
            nextMaintenance: '2026-10-30',
            prediction: 'Bearing wear detected - Schedule maintenance'
          },
          {
            id: 'MACHINE_003',
            name: 'Compressor #3',
            status: 'critical',
            sensors: [
              { type: 'vibration', value: 1.2, unit: 'g', status: 'critical', threshold: 0.5 },
              { type: 'temperature', value: 85.7, unit: '°C', status: 'critical', threshold: 70 },
              { type: 'current', value: 18.2, unit: 'A', status: 'critical', threshold: 15 }
            ],
            healthScore: 45,
            lastMaintenance: '2026-08-01',
            nextMaintenance: '2026-10-20',
            prediction: 'Immediate attention required - High risk of failure'
          },
          {
            id: 'MACHINE_004',
            name: 'Fresadora #4',
            status: 'operational',
            sensors: [
              { type: 'vibration', value: 0.2, unit: 'g', status: 'normal', threshold: 0.5 },
              { type: 'temperature', value: 58.3, unit: '°C', status: 'normal', threshold: 70 },
              { type: 'current', value: 10.8, unit: 'A', status: 'normal', threshold: 15 }
            ],
            healthScore: 95,
            lastMaintenance: '2026-09-20',
            nextMaintenance: '2026-12-01',
            prediction: 'Optimal performance - No issues detected'
          }
        ],
        alerts: [
          { id: 1, type: 'warning', message: 'High vibration detected on Injetora #2', timestamp: '2026-10-14T08:30:00Z', machineId: 'MACHINE_002' },
          { id: 2, type: 'critical', message: 'Temperature critical on Compressor #3', timestamp: '2026-10-14T09:15:00Z', machineId: 'MACHINE_003' },
          { id: 3, type: 'info', message: 'Scheduled maintenance for Torno CNC #1 in 30 days', timestamp: '2026-10-14T10:00:00Z', machineId: 'MACHINE_001' }
        ],
        stats: {
          totalMachines: 4,
          operational: 2,
          warning: 1,
          critical: 1,
          avgHealthScore: 76.75,
          predictionsAccuracy: 98,
          uptime: 99.5
        }
      };
      
      setSensorData(mockData);
      setLoading(false);
    };

    fetchSensorData();
  }, []);

  const products = [
    {
      id: 'autoatendimento',
      name: 'Autoatendimento Inteligente',
      description: 'Chatbots com IA generativa para atendimento multi-canal',
      icon: 'message-square',
      status: 'TRL 8',
      features: ['NLP avancado', 'Integracao com CRM', 'Automatizacao de fluxos'],
      link: '/solucoes/autoatendimento'
    },
    {
      id: 'gestao-vendas',
      name: 'Gestao de Vendas Avancada',
      description: 'Previsao de demanda e otimizacao de estoque com ML',
      icon: 'trending-up',
      status: 'TRL 8',
      features: ['Previsao de demanda', 'Otimizacao de estoque', 'Analise de clientes'],
      link: '/solucoes/gestao-vendas'
    },
    {
      id: 'dna-maquina',
      name: 'DNA de Maquinas',
      description: 'Monitoramento de equipamentos com sensores IoT e manutencao preditiva',
      icon: 'cpu',
      status: 'TRL 8',
      features: ['Sensores IoT', 'Manutencao preditiva', 'Alertas inteligentes'],
      link: '/solucoes/dna-maquina'
    },
    {
      id: 'pedido-sem-fronteiras',
      name: 'Pedidos Sem Fronteiras',
      description: 'Integracao multi-canal com logistica otimizada',
      icon: 'globe',
      status: 'TRL 8',
      features: ['Integracao multi-canal', 'Logistica otimizada', 'Rastreamento em tempo real'],
      link: '/solucoes/pedido-sem-fronteiras'
    },
    {
      id: 'observabilidade',
      name: 'Observabilidade Total',
      description: 'Monitoramento unificado com dashboards e alertas inteligentes',
      icon: 'eye',
      status: 'TRL 8',
      features: ['Dashboards unificados', 'Alertas baseados em ML', 'Tracing distribuido'],
      link: '/solucoes/observabilidade'
    },
    {
      id: 'ia-ml-sensores',
      name: 'IA/ML com Sensores',
      description: 'Processamento de dados de sensores com modelos de ML',
      icon: 'zap',
      status: 'TRL 8',
      features: ['Processamento em tempo real', 'Modelos de predicao', 'Integracao com Kiro'],
      link: '/solucoes/ia-ml-sensores'
    }
  ];

  const stats = [
    { label: 'Maquinas Monitoradas', value: sensorData?.stats.totalMachines || 0, unit: '', trend: 'up', change: '+12%' },
    { label: 'Disponibilidade', value: sensorData?.stats.uptime || 0, unit: '%', trend: 'up', change: '+0.5%' },
    { label: 'Precisao de Predicoes', value: sensorData?.stats.predictionsAccuracy || 0, unit: '%', trend: 'stable', change: '0%' },
    { label: 'Saude Media', value: sensorData?.stats.avgHealthScore || 0, unit: '/100', trend: 'down', change: '-2%' }
  ];

  return (
    <Layout title="CORETHREE3 - Plataforma de Solucoes Integradas">
      <div className="container">
        {/* Header */}
        <header className="py-lg">
          <div className="flex justify-between items-center mb-lg">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-sm">
                CORETHREE3
              </h1>
              <p className="text-gray-600">
                Plataforma TRL 8 para Automacao Industrial e Varejo Inteligente
              </p>
            </div>
            <div className="flex gap-md">
              <button 
                className={`btn ${activeTab === 'overview' ? 'btn-primary' : 'btn-outline'}`}
                onClick={() => setActiveTab('overview')}
              >
                Visao Geral
              </button>
              <button 
                className={`btn ${activeTab === 'sensors' ? 'btn-primary' : 'btn-outline'}`}
                onClick={() => setActiveTab('sensors')}
              >
                Sensores IoT
              </button>
              <button 
                className={`btn ${activeTab === 'products' ? 'btn-primary' : 'btn-outline'}`}
                onClick={() => setActiveTab('products')}
              >
                Produtos
              </button>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main>
          {activeTab === 'overview' && (
            <>
              {/* Stats Overview */}
              <StatsOverview stats={stats} loading={loading} />
              
              {/* Alerts Section */}
              <div className="mb-lg">
                <div className="flex justify-between items-center mb-md">
                  <h2 className="text-xl font-semibold text-gray-900">Alertas Recentes</h2>
                  <span className="badge badge-warning">
                    {sensorData?.alerts.filter(a => a.type === 'warning').length || 0} Avisos
                  </span>
                  <span className="badge badge-error">
                    {sensorData?.alerts.filter(a => a.type === 'critical').length || 0} Criticos
                  </span>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-md">
                  {sensorData?.alerts.map(alert => (
                    <div 
                      key={alert.id} 
                      className={`alert alert-${alert.type} animate-fade-in`}
                    >
                      <div className="flex justify-between items-start">
                        <div>
                          <h3 className="font-semibold text-gray-900 mb-xs">{alert.message}</h3>
                          <p className="text-sm text-gray-600">{alert.machineId}</p>
                        </div>
                        <span className="text-sm opacity-70">{new Date(alert.timestamp).toLocaleTimeString('pt-BR')}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              
              {/* Products Preview */}
              <div className="mb-lg">
                <h2 className="text-xl font-semibold text-gray-900 mb-md">Nossos Produtos</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-md">
                  {products.slice(0, 3).map(product => (
                    <div key={product.id} className="card animate-slide-in">
                      <div className="card-header">
                        <h3 className="card-title">{product.name}</h3>
                        <span className={`badge badge-${product.status === 'TRL 8' ? 'success' : 'info'}`}>
                          {product.status}
                        </span>
                      </div>
                      <div className="card-body">
                        <p className="text-gray-600 mb-md">{product.description}</p>
                        <ul className="text-sm text-gray-600 space-y-xs mb-md">
                          {product.features.map((feature, index) => (
                            <li key={index}>- {feature}</li>
                          ))}
                        </ul>
                        <button className="btn btn-outline btn-sm">
                          Ver Detalhes
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}

          {activeTab === 'sensors' && (
            <SensorDashboard data={sensorData} loading={loading} />
          )}

          {activeTab === 'products' && (
            <ProductGrid products={products} />
          )}
        </main>

        {/* Footer */}
        <footer className="py-lg mt-lg border-t border-gray-200">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-sm text-gray-500">
                CORETHREE3 - Plataforma TRL 8
              </p>
              <p className="text-xs text-gray-400">
                Integracao com Kiro (AWS AI Agent) | IA/ML | Sensores IoT
              </p>
            </div>
            <div className="flex gap-md text-sm text-gray-500">
              <a href="/docs" className="hover:text-primary">Documentacao</a>
              <a href="/solucoes" className="hover:text-primary">Solucoes</a>
              <a href="/contato" className="hover:text-primary">Contato</a>
            </div>
          </div>
        </footer>
      </div>
    </Layout>
  );
};

export default HomePage;
