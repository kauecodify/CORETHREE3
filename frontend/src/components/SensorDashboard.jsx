import React from 'react';

const SensorDashboard = ({ data, loading }) => {
  if (loading) {
    return (
      <div className="flex justify-center items-center py-xl">
        <div className="animate-pulse">
          <div className="w-12 h-12 bg-gray-300 rounded-full"></div>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="alert alert-info">
        Nenhum dado de sensores disponivel no momento.
      </div>
    );
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'operational':
        return 'success';
      case 'warning':
        return 'warning';
      case 'critical':
        return 'error';
      default:
        return 'info';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'operational':
        return 'Operacional';
      case 'warning':
        return 'Aviso';
      case 'critical':
        return 'Critico';
      default:
        return 'Desconhecido';
    }
  };

  return (
    <div className="space-y-lg">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-md">
        <div className="card">
          <div className="card-header">
            <h3 className="card-title text-sm">Total de Maquinas</h3>
          </div>
          <div className="card-body">
            <div className="text-3xl font-bold text-gray-900">{data.stats.totalMachines}</div>
            <div className="text-sm text-gray-500 mt-xs">Maquinas monitoradas</div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title text-sm">Operacionais</h3>
          </div>
          <div className="card-body">
            <div className="text-3xl font-bold text-success">{data.stats.operational}</div>
            <div className="text-sm text-gray-500 mt-xs">Maquinas normais</div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title text-sm">Em Aviso</h3>
          </div>
          <div className="card-body">
            <div className="text-3xl font-bold text-warning">{data.stats.warning}</div>
            <div className="text-sm text-gray-500 mt-xs">Maquinas com atencao</div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title text-sm">Criticas</h3>
          </div>
          <div className="card-body">
            <div className="text-3xl font-bold text-error">{data.stats.critical}</div>
            <div className="text-sm text-gray-500 mt-xs">Maquinas com problemas</div>
          </div>
        </div>
      </div>

      {/* Machines Table */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Status das Maquinas</h2>
        </div>
        <div className="card-body">
          <div className="overflow-x-auto">
            <table className="table">
              <thead>
                <tr>
                  <th>Maquina</th>
                  <th>Status</th>
                  <th>Saude</th>
                  <th>Vibracao</th>
                  <th>Temperatura</th>
                  <th>Corrente</th>
                  <th>Predicao</th>
                </tr>
              </thead>
              <tbody>
                {data.machines.map(machine => (
                  <tr key={machine.id}>
                    <td className="font-medium text-gray-900">{machine.name}</td>
                    <td>
                      <span className={`badge badge-${getStatusColor(machine.status)}`}>
                        {getStatusText(machine.status)}
                      </span>
                    </td>
                    <td>
                      <div className="flex items-center gap-xs">
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className={`bg-${getStatusColor(machine.status)} h-2 rounded-full`}
                            style={{ width: `${machine.healthScore}%` }}
                          ></div>
                        </div>
                        <span className="text-xs text-gray-500">{machine.healthScore}</span>
                      </div>
                    </td>
                    <td>
                      {machine.sensors.find(s => s.type === 'vibration') && (
                        <div className={`text-${getStatusColor(machine.sensors.find(s => s.type === 'vibration').status)}`}>
                          {machine.sensors.find(s => s.type === 'vibration').value} {machine.sensors.find(s => s.type === 'vibration').unit}
                        </div>
                      )}
                    </td>
                    <td>
                      {machine.sensors.find(s => s.type === 'temperature') && (
                        <div className={`text-${getStatusColor(machine.sensors.find(s => s.type === 'temperature').status)}`}>
                          {machine.sensors.find(s => s.type === 'temperature').value} {machine.sensors.find(s => s.type === 'temperature').unit}
                        </div>
                      )}
                    </td>
                    <td>
                      {machine.sensors.find(s => s.type === 'current') && (
                        <div className={`text-${getStatusColor(machine.sensors.find(s => s.type === 'current').status)}`}>
                          {machine.sensors.find(s => s.type === 'current').value} {machine.sensors.find(s => s.type === 'current').unit}
                        </div>
                      )}
                    </td>
                    <td className="text-sm text-gray-600">{machine.prediction}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Machine Details */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-md">
        {data.machines.slice(0, 2).map(machine => (
          <div key={machine.id} className="card">
            <div className="card-header">
              <h3 className="card-title">{machine.name}</h3>
              <span className={`badge badge-${getStatusColor(machine.status)}`}>
                {getStatusText(machine.status)}
              </span>
            </div>
            <div className="card-body">
              <div className="grid grid-cols-2 gap-md mb-md">
                <div>
                  <div className="text-sm text-gray-500 mb-xs">Saude</div>
                  <div className="text-2xl font-bold text-gray-900">{machine.healthScore}/100</div>
                </div>
                <div>
                  <div className="text-sm text-gray-500 mb-xs">Proxima Manutencao</div>
                  <div className="text-lg font-medium text-gray-900">{machine.nextMaintenance}</div>
                </div>
              </div>
              
              <div className="mb-md">
                <div className="text-sm text-gray-500 mb-xs">Sensores</div>
                <div className="space-y-xs">
                  {machine.sensors.map(sensor => (
                    <div 
                      key={sensor.type} 
                      className={`flex justify-between items-center p-sm rounded-md bg-${getStatusColor(sensor.status) === 'normal' ? 'gray-50' : getStatusColor(sensor.status) === 'warning' ? 'yellow-50' : 'red-50'}`}
                    >
                      <div>
                        <span className="text-sm font-medium text-gray-700">{sensor.type}</span>
                      </div>
                      <div className="flex items-center gap-sm">
                        <span className={`text-sm font-medium text-${getStatusColor(sensor.status)}`}>
                          {sensor.value} {sensor.unit}
                        </span>
                        <span className={`badge badge-${getStatusColor(sensor.status)} badge-xs`}>
                          {getStatusText(sensor.status)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="alert alert-info text-sm">
                {machine.prediction}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SensorDashboard;
