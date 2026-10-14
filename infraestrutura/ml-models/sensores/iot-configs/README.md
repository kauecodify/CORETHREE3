# Configuracoes de Sensores IoT - CORETHREE3

## Visao Geral

Este diretorio contem as configuracoes de sensores IoT para o modulo DNA de Maquinas e IA/ML do CORETHREE3. Os sensores sao dispositivos de baixo custo, alta precisao, projetados especificamente para monitoramento industrial.

---

## Estrutura

```
sensores/
└── iot-configs/
    ├── sensor_types.json          # Tipos de sensores suportados
    ├── sensor_configurations.json # Configuracoes padrao de sensores
    ├── calibration/
    │   ├── vibration_calibration.json # Calibracao de sensores de vibracao
    │   ├── temperature_calibration.json # Calibracao de sensores de temperatura
    │   ├── pressure_calibration.json # Calibracao de sensores de pressao
    │   └── current_calibration.json # Calibracao de sensores de corrente
    ├── deployment/
    │   ├── factory_deployment.json # Configuracao para deploy em fabrica
    │   ├── warehouse_deployment.json # Configuracao para deploy em armazen
    │   └── vehicle_deployment.json # Configuracao para deploy em veiculos
    ├── connectivity/
    │   ├── wifi_config.json      # Configuracao WiFi
    │   ├── bluetooth_config.json # Configuracao Bluetooth
    │   ├── lora_config.json      # Configuracao LoRaWAN
    │   └── cellular_config.json  # Configuracao Celular
    ├── security/
    │   ├── encryption_config.json # Configuracao de criptografia
    │   ├── authentication_config.json # Configuracao de autenticacao
    │   └── access_control_config.json # Configuracao de controle de acesso
    └── README.md                 # Este documento
```

---

## Tipos de Sensores

### sensor_types.json

```json
{
  "sensors": [
    {
      "id": "vibration",
      "name": "Sensor de Vibracao",
      "description": "Monitoramento de vibracao em maquinas rotativas",
      "type": "accelerometer",
      "axis": 3,
      "range": "0-10kHz",
      "precision": "+/-0.1%",
      "sampling_rate": "1kHz",
      "power_consumption": "0.5W",
      "battery_life": "5 years",
      "cost": 75.00,
      "applications": [
        "motors",
        "pumps",
        "compressors",
        "fans",
        "gearboxes"
      ],
      "detection_capabilities": [
        "imbalance",
        "bearing_failure",
        "misalignment",
        "looseness",
        "cavitation"
      ]
    },
    {
      "id": "temperature",
      "name": "Sensor de Temperatura",
      "description": "Monitoramento de temperatura em equipamentos e ambientes",
      "type": "thermocouple",
      "range": "-50 to 200C",
      "precision": "+/-0.5C",
      "sampling_rate": "10Hz",
      "power_consumption": "0.3W",
      "battery_life": "5 years",
      "cost": 50.00,
      "applications": [
        "motors",
        "bearings",
        "pipes",
        "storage",
        "environmental"
      ],
      "detection_capabilities": [
        "overheating",
        "temperature_trends",
        "thermal_expansion",
        "cooling_efficiency"
      ]
    },
    {
      "id": "pressure",
      "name": "Sensor de Pressao",
      "description": "Monitoramento de pressao em sistemas hidraulicos e pneumáticos",
      "type": "piezoresistive",
      "range": "0-100bar",
      "precision": "+/-0.2%",
      "sampling_rate": "100Hz",
      "power_consumption": "0.4W",
      "battery_life": "5 years",
      "cost": 60.00,
      "applications": [
        "hydraulic_systems",
        "pneumatic_systems",
        "pipes",
        "tanks",
        "valves"
      ],
      "detection_capabilities": [
        "leaks",
        "blockages",
        "pressure_drops",
        "pressure_spikes",
        "cavitation"
      ]
    },
    {
      "id": "humidity",
      "name": "Sensor de Umidade",
      "description": "Monitoramento de umidade em ambientes e materiais",
      "type": "capacitive",
      "range": "0-100%",
      "precision": "+/-2%",
      "sampling_rate": "1Hz",
      "power_consumption": "0.2W",
      "battery_life": "5 years",
      "cost": 40.00,
      "applications": [
        "storage",
        "production",
        "warehouses",
        "greenhouses",
        "laboratories"
      ],
      "detection_capabilities": [
        "condensation",
        "mold_risk",
        "drying_efficiency",
        "environmental_control"
      ]
    },
    {
      "id": "current",
      "name": "Sensor de Corrente Eletrica",
      "description": "Monitoramento de consumo de corrente em equipamentos eletricos",
      "type": "hall_effect",
      "range": "0-100A",
      "precision": "+/-0.5%",
      "sampling_rate": "1kHz",
      "power_consumption": "0.5W",
      "battery_life": "5 years",
      "cost": 80.00,
      "applications": [
        "motors",
        "generators",
        "transformers",
        "circuit_breakers",
        "electrical_panels"
      ],
      "detection_capabilities": [
        "overload",
        "short_circuit",
        "power_quality",
        "energy_consumption",
        "efficiency"
      ]
    },
    {
      "id": "gps",
      "name": "Sensor GPS",
      "description": "Rastreamento de localizacao de veiculos e equipamentos",
      "type": "gnss",
      "precision": "+/-5m",
      "sampling_rate": "1Hz",
      "power_consumption": "0.8W",
      "battery_life": "3 years",
      "cost": 120.00,
      "applications": [
        "vehicles",
        "containers",
        "equipment",
        "assets"
      ],
      "detection_capabilities": [
        "location",
        "speed",
        "direction",
        "geofencing",
        "route_deviation"
      ]
    }
  ]
}
```

---

## Configuracoes Padrao de Sensores

### sensor_configurations.json

```json
{
  "default_configurations": {
    "vibration": {
      "sampling_rate": 1000,
      "sensitivity": "high",
      "filter": {
        "enabled": true,
        "type": "low_pass",
        "cutoff_frequency": 10000
      },
      "thresholds": {
        "warning": 0.5,
        "critical": 1.0
      },
      "calibration": {
        "offset": 0.0,
        "scale": 1.0
      },
      "alerts": {
        "enabled": true,
        "severity": "high",
        "channels": ["email", "sms"]
      }
    },
    "temperature": {
      "sampling_rate": 10,
      "sensitivity": "medium",
      "filter": {
        "enabled": true,
        "type": "moving_average",
        "window_size": 5
      },
      "thresholds": {
        "warning": 70,
        "critical": 90
      },
      "unit": "celsius",
      "calibration": {
        "offset": 0.0,
        "scale": 1.0
      },
      "alerts": {
        "enabled": true,
        "severity": "medium",
        "channels": ["email"]
      }
    },
    "pressure": {
      "sampling_rate": 100,
      "sensitivity": "high",
      "filter": {
        "enabled": true,
        "type": "kalman",
        "noise": 0.1
      },
      "thresholds": {
        "warning": 50,
        "critical": 80
      },
      "unit": "bar",
      "calibration": {
        "offset": 0.0,
        "scale": 1.0
      },
      "alerts": {
        "enabled": true,
        "severity": "high",
        "channels": ["email", "sms"]
      }
    },
    "humidity": {
      "sampling_rate": 1,
      "sensitivity": "medium",
      "filter": {
        "enabled": true,
        "type": "exponential_smoothing",
        "alpha": 0.3
      },
      "thresholds": {
        "warning": 60,
        "critical": 80
      },
      "unit": "percent",
      "calibration": {
        "offset": 0.0,
        "scale": 1.0
      },
      "alerts": {
        "enabled": true,
        "severity": "low",
        "channels": ["email"]
      }
    },
    "current": {
      "sampling_rate": 1000,
      "sensitivity": "high",
      "filter": {
        "enabled": true,
        "type": "low_pass",
        "cutoff_frequency": 100
      },
      "thresholds": {
        "warning": 80,
        "critical": 100
      },
      "unit": "ampere",
      "calibration": {
        "offset": 0.0,
        "scale": 1.0
      },
      "alerts": {
        "enabled": true,
        "severity": "critical",
        "channels": ["email", "sms", "slack"]
      }
    },
    "gps": {
      "sampling_rate": 1,
      "sensitivity": "medium",
      "filter": {
        "enabled": true,
        "type": "kalman",
        "noise": 5.0
      },
      "thresholds": {
        "geofence": {
          "enabled": true,
          "radius": 100
        },
        "speed": {
          "warning": 100,
          "critical": 120
        }
      },
      "unit": "meters",
      "calibration": {
        "offset": 0.0,
        "scale": 1.0
      },
      "alerts": {
        "enabled": true,
        "severity": "medium",
        "channels": ["email", "sms"]
      }
    }
  }
}
```

---

## Calibracao de Sensores

### vibration_calibration.json

```json
{
  "sensor_type": "vibration",
  "calibration_procedure": {
    "steps": [
      {
        "step": 1,
        "description": "Montar sensor na maquina em posicao padrao",
        "tools_required": ["chave_allen", "nivel"],
        "time_required": "5 minutes"
      },
      {
        "step": 2,
        "description": "Ligar maquina e aguardar estabilizacao",
        "operating_condition": "normal_operation",
        "time_required": "10 minutes"
      },
      {
        "step": 3,
        "description": "Executar rotina de calibracao automatica",
        "command": "calibrate --type vibration --mode auto",
        "time_required": "2 minutes"
      },
      {
        "step": 4,
        "description": "Verificar valores de referencia",
        "expected_values": {
          "x_axis": {"min": -0.1, "max": 0.1},
          "y_axis": {"min": -0.1, "max": 0.1},
          "z_axis": {"min": -0.1, "max": 0.1}
        },
        "tolerance": 0.05
      }
    ],
    "total_time": "20 minutes",
    "required_environment": "controlled"
  },
  "calibration_parameters": {
    "offset": {
      "x_axis": 0.0,
      "y_axis": 0.0,
      "z_axis": 0.0
    },
    "scale": {
      "x_axis": 1.0,
      "y_axis": 1.0,
      "z_axis": 1.0
    },
    "temperature_compensation": true,
    "sensitivity_adjustment": 1.0
  },
  "verification": {
    "enabled": true,
    "frequency": "7d",
    "tolerance": 0.02,
    "alert_on_drift": true
  },
  "documentation": {
    "calibration_certificate": true,
    "report_format": "pdf",
    "storage_location": "s3://corethree3-calibration/vibration/"
  }
}
```

### temperature_calibration.json

```json
{
  "sensor_type": "temperature",
  "calibration_procedure": {
    "steps": [
      {
        "step": 1,
        "description": "Preparar banho termico com temperatura de referencia",
        "tools_required": ["banho_termico", "termometro_padrao"],
        "time_required": "10 minutes"
      },
      {
        "step": 2,
        "description": "Inserir sensor no banho termico",
        "immersion_depth": "10cm",
        "time_required": "2 minutes"
      },
      {
        "step": 3,
        "description": "Aguardar estabilizacao termica",
        "stabilization_time": "15 minutes",
        "tolerance": 0.1
      },
      {
        "step": 4,
        "description": "Registrar leituras em multiplos pontos",
        "reference_points": [0, 25, 50, 75, 100],
        "readings_per_point": 5,
        "time_required": "10 minutes"
      },
      {
        "step": 5,
        "description": "Calcular curva de calibracao",
        "method": "linear_regression",
        "time_required": "1 minute"
      }
    ],
    "total_time": "40 minutes",
    "required_environment": "laboratory"
  },
  "calibration_parameters": {
    "offset": 0.0,
    "scale": 1.0,
    "nonlinearity_correction": {
      "enabled": true,
      "coefficients": [0.0, 1.0, 0.0]
    },
    "temperature_compensation": false
  },
  "verification": {
    "enabled": true,
    "frequency": "30d",
    "tolerance": 0.5,
    "alert_on_drift": true
  },
  "documentation": {
    "calibration_certificate": true,
    "report_format": "pdf",
    "storage_location": "s3://corethree3-calibration/temperature/"
  }
}
```

---

## Configuracoes de Conectividade

### wifi_config.json

```json
{
  "connectivity_type": "wifi",
  "supported_standards": ["802.11b", "802.11g", "802.11n", "802.11ac"],
  "frequency_bands": ["2.4GHz", "5GHz"],
  "security_protocols": ["WPA2-PSK", "WPA3-PSK", "WPA2-Enterprise"],
  "configuration": {
    "ssid": "CORETHREE3_IoT",
    "password": "${WIFI_PASSWORD}",
    "security": "WPA2-PSK",
    "auto_connect": true,
    "retry_policy": {
      "max_retries": 5,
      "retry_interval": 10000
    }
  },
  "performance": {
    "power_consumption": {
      "idle": "0.1W",
      "active": "0.5W"
    },
    "data_rate": {
      "max": "100Mbps",
      "typical": "50Mbps"
    },
    "latency": {
      "min": 1,
      "max": 100,
      "typical": 10
    }
  },
  "fallback": {
    "enabled": true,
    "strategy": "switch_to_cellular",
    "threshold": 3
  },
  "monitoring": {
    "enabled": true,
    "metrics": ["signal_strength", "connection_stability", "data_rate"],
    "alerts": {
      "low_signal": {
        "threshold": -70,
        "severity": "warning"
      },
      "connection_lost": {
        "severity": "critical"
      }
    }
  }
}
```

### bluetooth_config.json

```json
{
  "connectivity_type": "bluetooth",
  "supported_versions": ["4.0", "4.1", "4.2", "5.0", "5.1"],
  "configuration": {
    "device_name": "CORETHREE3_Sensor",
    "pairing_mode": "just_works",
    "auto_pairing": true,
    "bonding": true,
    "encryption": true
  },
  "performance": {
    "power_consumption": {
      "advertising": "0.01W",
      "connected": "0.1W"
    },
    "data_rate": {
      "max": "3Mbps",
      "typical": "1Mbps"
    },
    "range": {
      "indoor": "20m",
      "outdoor": "100m"
    },
    "latency": {
      "min": 1,
      "max": 50,
      "typical": 10
    }
  },
  "profiles": [
    {
      "name": "data_transfer",
      "uuid": "00001101-0000-1000-8000-00805f9b34fb",
      "description": "Transferencia de dados de sensores"
    },
    {
      "name": "device_information",
      "uuid": "0000180a-0000-1000-8000-00805f9b34fb",
      "description": "Informacoes do dispositivo"
    }
  ],
  "security": {
    "encryption": true,
    "authentication": true,
    "secure_connections_only": true
  },
  "monitoring": {
    "enabled": true,
    "metrics": ["signal_strength", "connection_stability"],
    "alerts": {
      "connection_lost": {
        "severity": "warning"
      }
    }
  }
}
```

### lora_config.json

```json
{
  "connectivity_type": "lora",
  "supported_frequencies": ["868MHz", "915MHz"],
  "configuration": {
    "region": "LATAM",
    "frequency": "915MHz",
    "spreading_factor": 7,
    "bandwidth": 125,
    "coding_rate": "4/5",
    "join_mode": "OTAA",
    "dev_eui": "${DEV_EUI}",
    "app_eui": "${APP_EUI}",
    "app_key": "${APP_KEY}"
  },
  "performance": {
    "power_consumption": {
      "transmit": "0.5W",
      "receive": "0.1W",
      "sleep": "0.001W"
    },
    "data_rate": {
      "max": "50kbps",
      "typical": "10kbps"
    },
    "range": {
      "urban": "2km",
      "suburban": "5km",
      "rural": "15km"
    },
    "latency": {
      "min": 100,
      "max": 10000,
      "typical": 2000
    }
  },
  "duty_cycle": {
    "enabled": true,
    "max": 1,
    "typical": 0.1
  },
  "security": {
    "encryption": true,
    "message_integrity_code": true
  },
  "monitoring": {
    "enabled": true,
    "metrics": ["signal_strength", "packet_loss", "latency"],
    "alerts": {
      "low_signal": {
        "threshold": -120,
        "severity": "warning"
      },
      "high_packet_loss": {
        "threshold": 10,
        "severity": "warning"
      },
      "connection_lost": {
        "severity": "critical"
      }
    }
  }
}
```

---

## Configuracoes de Seguranca

### encryption_config.json

```json
{
  "encryption": {
    "enabled": true,
    "algorithm": "AES-256-GCM",
    "key_management": {
      "type": "aws_kms",
      "key_id": "${KMS_KEY_ID}",
      "key_rotation": {
        "enabled": true,
        "frequency": "365d"
      }
    },
    "data_types": [
      "sensor_data",
      "device_commands",
      "configuration_data",
      "firmware_updates"
    ],
    "performance": {
      "encryption_speed": "100Mbps",
      "decryption_speed": "100Mbps"
    }
  },
  "secure_communication": {
    "tls": {
      "enabled": true,
      "version": "1.3",
      "cipher_suites": [
        "TLS_AES_256_GCM_SHA384",
        "TLS_CHACHA20_POLY1305_SHA256",
        "TLS_AES_128_GCM_SHA256"
      ],
      "certificate_validation": true
    },
    "mqtt": {
      "enabled": true,
      "protocol": "MQTT over TLS",
      "port": 8883
    }
  },
  "data_integrity": {
    "enabled": true,
    "hash_algorithm": "SHA-256",
    "signature": true
  }
}
```

### authentication_config.json

```json
{
  "authentication": {
    "methods": [
      {
        "type": "x509_certificate",
        "enabled": true,
        "certificate_authority": "${CA_NAME}",
        "certificate_lifetime": "365d",
        "revocation_check": true
      },
      {
        "type": "api_key",
        "enabled": true,
        "key_length": 64,
        "key_lifetime": "30d",
        "rotation": {
          "enabled": true,
          "frequency": "30d"
        }
      },
      {
        "type": "jwt",
        "enabled": true,
        "algorithm": "RS256",
        "key_size": 2048,
        "token_lifetime": "1h",
        "refresh_token_lifetime": "7d"
      },
      {
        "type": "iot_core",
        "enabled": true,
        "certificate_lifetime": "365d",
        "policy_attached": true
      }
    ],
    "multi_factor": {
      "enabled": false,
      "methods": ["totp", "sms", "email"]
    },
    "rate_limiting": {
      "enabled": true,
      "max_attempts": 5,
      "lockout_duration": 300
    }
  },
  "authorization": {
    "model": "RBAC",
    "roles": [
      {
        "name": "admin",
        "permissions": ["*"],
        "resources": ["*"]
      },
      {
        "name": "operator",
        "permissions": ["read", "write"],
        "resources": ["sensors", "devices"]
      },
      {
        "name": "viewer",
        "permissions": ["read"],
        "resources": ["sensors", "devices", "data"]
      }
    ],
    "policies": {
      "default_deny": true,
      "least_privilege": true
    }
  },
  "audit": {
    "enabled": true,
    "logging": {
      "authentication_events": true,
      "authorization_events": true,
      "configuration_changes": true
    },
    "retention": "365d",
    "storage": "cloudwatch"
  }
}
```

---

## Configuracoes de Deploy

### factory_deployment.json

```json
{
  "deployment_type": "factory",
  "environment": "industrial",
  "requirements": {
    "power": "220V AC, 50Hz",
    "network": "Ethernet or WiFi",
    "space": "1m x 1m x 1m",
    "temperature": "-10 to 50C",
    "humidity": "10-90%"
  },
  "sensor_placement": {
    "vibration": {
      "location": "machine_casing",
      "orientation": "perpendicular_to_axis",
      "mounting": "magnetic_base",
      "quantity": 2
    },
    "temperature": {
      "location": "near_bearing",
      "mounting": "probe",
      "quantity": 1
    },
    "current": {
      "location": "power_cable",
      "mounting": "clamp_on",
      "quantity": 1
    }
  },
  "connectivity": {
    "primary": "wifi",
    "fallback": "cellular",
    "redundancy": true
  },
  "power": {
    "source": "main_power",
    "backup": "battery",
    "battery_life": "24h"
  },
  "monitoring": {
    "enabled": true,
    "metrics": [
      "sensor_health",
      "connectivity_status",
      "power_status",
      "data_quality"
    ],
    "alerts": {
      "sensor_failure": {
        "severity": "critical",
        "channels": ["email", "sms", "slack"]
      },
      "connectivity_loss": {
        "severity": "high",
        "channels": ["email", "sms"]
      },
      "low_battery": {
        "threshold": 20,
        "severity": "warning",
        "channels": ["email"]
      }
    }
  },
  "maintenance": {
    "schedule": "monthly",
    "procedures": [
      "sensor_calibration",
      "connectivity_test",
      "firmware_update",
      "battery_replacement"
    ]
  }
}
```

### warehouse_deployment.json

```json
{
  "deployment_type": "warehouse",
  "environment": "storage",
  "requirements": {
    "power": "110V/220V AC, 50/60Hz",
    "network": "WiFi or LoRaWAN",
    "space": "0.5m x 0.5m x 0.5m",
    "temperature": "0 to 40C",
    "humidity": "10-80%"
  },
  "sensor_placement": {
    "temperature": {
      "location": "ceiling",
      "height": "3m",
      "spacing": "10m",
      "quantity": "variable"
    },
    "humidity": {
      "location": "ceiling",
      "height": "3m",
      "spacing": "10m",
      "quantity": "variable"
    },
    "gps": {
      "location": "entry_points",
      "quantity": 1
    }
  },
  "connectivity": {
    "primary": "lora",
    "fallback": "wifi",
    "redundancy": false
  },
  "power": {
    "source": "battery",
    "battery_life": "5 years",
    "low_battery_alert": true
  },
  "monitoring": {
    "enabled": true,
    "metrics": [
      "temperature",
      "humidity",
      "connectivity_status",
      "battery_level"
    ],
    "alerts": {
      "temperature_out_of_range": {
        "threshold": [0, 40],
        "severity": "high",
        "channels": ["email", "sms"]
      },
      "humidity_out_of_range": {
        "threshold": [10, 80],
        "severity": "medium",
        "channels": ["email"]
      },
      "connectivity_loss": {
        "severity": "high",
        "channels": ["email", "sms"]
      },
      "low_battery": {
        "threshold": 20,
        "severity": "warning",
        "channels": ["email"]
      }
    }
  },
  "maintenance": {
    "schedule": "quarterly",
    "procedures": [
      "sensor_calibration",
      "battery_check",
      "connectivity_test"
    ]
  }
}
```

---

## Boas Praticas

### 1. Selecao de Sensores

- Escolha sensores com base na aplicacao especifica
- Considere ambiente de operacao (temperatura, umidade, vibracao)
- Verifique compatibilidade com sistemas existentes

### 2. Instalacao

- Siga procedimentos de calibracao
- Posicione sensores em locais representativos
- Teste conectividade antes da instalacao final

### 3. Configuracao

- Ajuste limiares de alerta de acordo com a aplicacao
- Configure redundancia de conectividade quando critico
- Habilite monitoramento de status dos sensores

### 4. Manutencao

- Realize calibracao periodica
- Monitore vida util das baterias
- Atualize firmware regularmente

---

## Integracao com CORETHREE3

Os sensores IoT se integram com os seguintes modulos do CORETHREE3:

1. **DNA de Maquinas:**
   - Monitoramento de equipamentos
   - Manutencao preditiva

2. **IA/ML:**
   - Processamento de dados
   - Modelos de predicao

3. **Observabilidade:**
   - Monitoramento de status
   - Alertas de problemas

---

## Suporte

Para suporte sobre configuracoes de sensores IoT:

- **Email:** support-iot@corethree3.com
- **Documentacao:** [https://docs.corethree3.com/iot-sensors](https://docs.corethree3.com/iot-sensors)
- **Issues:** [GitHub Issues](https://github.com/kauecodify/CORETHREE3/issues)

---

**Versao:** 1.0.0  
**Ultima Atualizacao:** Outubro 2026  
**Licenca:** BSD 3-Clause  
**Autor:** Equipe CORETHREE3
