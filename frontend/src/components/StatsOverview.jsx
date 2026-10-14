import React from 'react';

const StatsOverview = ({ stats, loading }) => {
  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'up':
        return '↑';
      case 'down':
        return '↓';
      case 'stable':
        return '→';
      default:
        return '';
    }
  };

  const getTrendColor = (trend) => {
    switch (trend) {
      case 'up':
        return 'text-success';
      case 'down':
        return 'text-error';
      case 'stable':
        return 'text-gray-500';
      default:
        return 'text-gray-500';
    }
  };

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-md mb-lg">
        {[1, 2, 3, 4].map((item) => (
          <div key={item} className="card">
            <div className="card-header">
              <div className="w-full h-4 bg-gray-200 rounded animate-pulse"></div>
            </div>
            <div className="card-body">
              <div className="w-16 h-16 bg-gray-200 rounded-full animate-pulse mb-sm"></div>
              <div className="w-full h-4 bg-gray-200 rounded animate-pulse"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-md mb-lg">
      {stats.map((stat, index) => (
        <div key={index} className="card animate-fade-in" style={{ animationDelay: `${index * 100}ms` }}>
          <div className="card-header">
            <h3 className="card-title text-sm">{stat.label}</h3>
          </div>
          <div className="card-body">
            <div className="flex items-center gap-md">
              <div>
                <div className="text-3xl font-bold text-gray-900">
                  {stat.value}
                  <span className="text-lg font-normal">{stat.unit}</span>
                </div>
                <div className={`text-sm ${getTrendColor(stat.trend)} mt-xs`}>
                  {getTrendIcon(stat.trend)} {stat.change}
                </div>
              </div>
              <div className="flex-1">
                {stat.trend === 'up' && (
                  <svg className="w-full h-16 text-success opacity-20" viewBox="0 0 100 40" preserveAspectRatio="none">
                    <path d="M0,20 L20,10 L40,20 L60,5 L80,25 L100,15" stroke="currentColor" strokeWidth="2" fill="none" />
                  </svg>
                )}
                {stat.trend === 'down' && (
                  <svg className="w-full h-16 text-error opacity-20" viewBox="0 0 100 40" preserveAspectRatio="none">
                    <path d="M0,20 L20,30 L40,20 L60,35 L80,15 L100,25" stroke="currentColor" strokeWidth="2" fill="none" />
                  </svg>
                )}
                {stat.trend === 'stable' && (
                  <svg className="w-full h-16 text-gray-400 opacity-20" viewBox="0 0 100 40" preserveAspectRatio="none">
                    <path d="M0,20 L100,20" stroke="currentColor" strokeWidth="2" fill="none" />
                  </svg>
                )}
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default StatsOverview;
