
import requests
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from datetime import timedelta

DOMAIN = 'fipe_car'

CONF_MARCA = 'marca'
CONF_VEICULO = 'veiculo'
CONF_ANO_MODELO = 'ano_modelo'
CONF_COMBUSTIVEL = 'combustivel'

DEFAULT_NAME = 'FIPE Car'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Required(CONF_MARCA): cv.string,
        vol.Required(CONF_VEICULO): cv.string,
        vol.Required(CONF_ANO_MODELO): cv.string,
        vol.Required(CONF_COMBUSTIVEL): cv.string
    })
}, extra=vol.ALLOW_EXTRA)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the FIPE car platform."""
    name = config[DOMAIN].get(CONF_NAME)
    marca = config[DOMAIN].get(CONF_MARCA)
    veiculo = config[DOMAIN].get(CONF_VEICULO)
    ano_modelo = config[DOMAIN].get(CONF_ANO_MODELO)
    combustivel = config[DOMAIN].get(CONF_COMBUSTIVEL)

    sensor = FIPECarSensor(name, marca, veiculo, ano_modelo, combustivel)
    sensor.update()  # Atualiza imediatamente ao ser inicializado
    add_entities([sensor])


class FIPECarSensor(Entity):
    """Representation of a FIPE car sensor."""

    def __init__(self, name, marca, veiculo, ano_modelo, combustivel):
        """Initialize the sensor."""
        self._name = name
        self._marca = marca
        self._veiculo = veiculo
        self._ano_modelo = ano_modelo
        self._combustivel = combustivel
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    def update(self):
        """Fetch data from FIPE API."""
        url = f"https://parallelum.com.br/fipe/api/v1/carros/marcas/{self._marca}/modelos/{self._veiculo}/anos/{self._ano_modelo}-{self._combustivel}"
        headers = {
            "Referer": "https://veiculos.fipe.org.br/"
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            valor = data['Valor']
            marca = data['Marca']
            modelo = data['Modelo']
            ano = data['AnoModelo']
            combustivel = data['Combustivel']
            self._state = f"Marca: {marca}, Modelo: {modelo}, Ano: {ano}, Combustível: {combustivel}, Valor: R${valor}"
        else:
            self._state = "Erro ao consultar a FIPE"

        # Agendar próxima atualização em 1 hora
        self.schedule_update_ha_state(timedelta(hours=1))
