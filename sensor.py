import logging

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.const import DEVICE_CLASS_ENERGY, ENERGY_KILO_WATT_HOUR

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add sensors for passed config_entry in HA."""
    _LOGGER.warning("Start setup sensor")
    hub = hass.data[DOMAIN][config_entry.entry_id]

    new_devices = []
    for board in hub.boards:
        new_devices.append(ProductionTodaySensor(board))
        new_devices.append(ConsumptionTodaySensor(board))
        new_devices.append(OwnConsumptionTodaySensor(board))
        new_devices.append(ToGridTodaySensor(board))
        new_devices.append(FromGridTodaySensor(board))

        new_devices.append(ProductionTotalSensor(board))
        new_devices.append(ConsumptionTotalSensor(board))
        new_devices.append(OwnConsumptionSensor(board))
        new_devices.append(ToGridTotalSensor(board))
        new_devices.append(FromGridTotalSensor(board))

        new_devices.append(ToCompensate(board))
        new_devices.append(TokensToBurn(board))

        new_devices.append(Compensated(board))
        new_devices.append(LastHash(board))
        new_devices.append(Link(board))
    if new_devices:
        async_add_entities(new_devices)


class SensorBase(SensorEntity):

    should_poll = False

    def __init__(self, board):
        """Initialize the sensor."""
        self._board = board

    @property
    def device_info(self):
        """Return information to link this entity with the correct device."""
        return {"identifiers": {(DOMAIN, self._board.board_id)}}

    @property
    def available(self) -> bool:
        """Return True if board and hub is available."""
        return True

    async def async_added_to_hass(self):
        """Run when this Entity has been added to HA."""
        self._board.register_callback(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        """Entity being removed from hass."""
        self._board.remove_callback(self.async_write_ha_state)


class ToGridTodaySensor(SensorBase):
    def __init__(self, board):
        """Initialize the sensor."""
        super().__init__(board)

        self._attr_unique_id = f"{self._board.board_id}_to_grid_today"

        # The name of the entity
        self._attr_name = f"{self._board.name} To Grid Today"
        self.entity_description = SensorEntityDescription(
            key="setpoint",
            name=self._attr_name,
            native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
            device_class=DEVICE_CLASS_ENERGY,
            state_class=SensorStateClass.MEASUREMENT,
        )

    @property
    def state(self):
        """Return the state of the sensor."""

        return self._board._to_grid_today


class FromGridTodaySensor(SensorBase):
    def __init__(self, board):
        """Initialize the sensor."""
        super().__init__(board)

        self._attr_unique_id = f"{self._board.board_id}_from_grid_today"

        # The name of the entity
        self._attr_name = f"{self._board.name} From Grid Today"
        self.entity_description = SensorEntityDescription(
            key="setpoint",
            name=self._attr_name,
            native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
            device_class=DEVICE_CLASS_ENERGY,
            state_class=SensorStateClass.MEASUREMENT,
        )

    @property
    def state(self):
        """Return the state of the sensor."""

        return self._board._from_grid_today


class ProductionTodaySensor(SensorBase):
    def __init__(self, board):
        """Initialize the sensor."""
        super().__init__(board)

        self._attr_unique_id = f"{self._board.board_id}_production_today"

        # The name of the entity
        self._attr_name = f"{self._board.name} Production Today"
        self.entity_description = SensorEntityDescription(
            key="setpoint",
            name=self._attr_name,
            native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
            device_class=DEVICE_CLASS_ENERGY,
            state_class=SensorStateClass.MEASUREMENT,
        )

    @property
    def state(self):
        """Return the state of the sensor."""

        return self._board._production


class ConsumptionTodaySensor(SensorBase):
    def __init__(self, board):
        """Initialize the sensor."""
        super().__init__(board)

        self._attr_unique_id = f"{self._board.board_id}_consumption_today"

        # The name of the entity
        self._attr_name = f"{self._board.name} Consumption Today"
        self.entity_description = SensorEntityDescription(
            key="setpoint",
            name=self._attr_name,
            native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
            device_class=DEVICE_CLASS_ENERGY,
            state_class=SensorStateClass.MEASUREMENT,
        )

    @property
    def state(self):
        """Return the state of the sensor."""

        return self._board._consumption


class OwnConsumptionTodaySensor(SensorBase):
    def __init__(self, board):
        """Initialize the sensor."""
        super().__init__(board)

        self._attr_unique_id = f"{self._board.board_id}_own_consumption_today"

        # The name of the entity
        self._attr_name = f"{self._board.name} Own Consumption Today"
        self.entity_description = SensorEntityDescription(
            key="setpoint",
            name=self._attr_name,
            native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
            device_class=DEVICE_CLASS_ENERGY,
            state_class=SensorStateClass.MEASUREMENT,
        )

    @property
    def state(self):
        """Return the state of the sensor."""

        return self._board._own_consumption


class ToGridTotalSensor(SensorBase):
    def __init__(self, board):
        """Initialize the sensor."""
        super().__init__(board)

        self._attr_unique_id = f"{self._board.board_id}_to_grid_total"

        # The name of the entity
        self._attr_name = f"{self._board.name} To Grid Total"
        self.entity_description = SensorEntityDescription(
            key="setpoint",
            name=self._attr_name,
            native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
            device_class=DEVICE_CLASS_ENERGY,
            state_class=SensorStateClass.TOTAL,
        )

    @property
    def state(self):
        """Return the state of the sensor."""

        return self._board._to_grid_total


class FromGridTotalSensor(SensorBase):
    def __init__(self, board):
        """Initialize the sensor."""
        super().__init__(board)

        self._attr_unique_id = f"{self._board.board_id}_from_grid_total"

        # The name of the entity
        self._attr_name = f"{self._board.name} From Grid Total"
        self.entity_description = SensorEntityDescription(
            key="setpoint",
            name=self._attr_name,
            native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
            device_class=DEVICE_CLASS_ENERGY,
            state_class=SensorStateClass.TOTAL,
        )

    @property
    def state(self):
        """Return the state of the sensor."""

        return self._board._from_grid_total


class ProductionTotalSensor(SensorBase):
    def __init__(self, board):
        """Initialize the sensor."""
        super().__init__(board)

        self._attr_unique_id = f"{self._board.board_id}_production_total"

        # The name of the entity
        self._attr_name = f"{self._board.name} Production Total"
        self.entity_description = SensorEntityDescription(
            key="setpoint",
            name=self._attr_name,
            native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
            device_class=DEVICE_CLASS_ENERGY,
            state_class=SensorStateClass.TOTAL,
        )

    @property
    def state(self):
        """Return the state of the sensor."""

        return self._board._production_total


class ConsumptionTotalSensor(SensorBase):
    def __init__(self, board):
        """Initialize the sensor."""
        super().__init__(board)

        self._attr_unique_id = f"{self._board.board_id}_consumption_total"

        # The name of the entity
        self._attr_name = f"{self._board.name} Consumption Total"
        self.entity_description = SensorEntityDescription(
            key="setpoint",
            name=self._attr_name,
            native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
            device_class=DEVICE_CLASS_ENERGY,
            state_class=SensorStateClass.TOTAL,
        )

    @property
    def state(self):
        """Return the state of the sensor."""

        return self._board._consumption_total


class OwnConsumptionSensor(SensorBase):
    def __init__(self, board):
        """Initialize the sensor."""
        super().__init__(board)

        self._attr_unique_id = f"{self._board.board_id}_own_consumption_total"

        # The name of the entity
        self._attr_name = f"{self._board.name} Own Consumption Total"
        self.entity_description = SensorEntityDescription(
            key="setpoint",
            name=self._attr_name,
            native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
            device_class=DEVICE_CLASS_ENERGY,
            state_class=SensorStateClass.TOTAL,
        )

    @property
    def state(self):
        """Return the state of the sensor."""

        return self._board._own_consumption_total


class Compensated(SensorBase):
    def __init__(self, board):
        """Initialize the sensor."""
        super().__init__(board)

        self._attr_unique_id = f"{self._board.board_id}_compensated"

        # The name of the entity
        self._attr_name = f"{self._board.name} Compensated"
        self.entity_description = SensorEntityDescription(
            key="setpoint",
            name=self._attr_name,
            native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
            device_class=DEVICE_CLASS_ENERGY,
            state_class=SensorStateClass.MEASUREMENT,
        )

    @property
    def state(self):
        """Return the state of the sensor."""

        return self._board._compensated


class LastHash(SensorBase):
    def __init__(self, board):
        """Initialize the sensor."""
        super().__init__(board)

        self._attr_unique_id = f"{self._board.board_id}_last_hash"

        # The name of the entity
        self._attr_name = f"{self._board.name} transaction hash"
        self.entity_description = SensorEntityDescription(
            key="setpoint",
            name=self._attr_name,
        )

    @property
    def state(self):
        """Return the state of the sensor."""

        return self._board._last_hash


class Link(SensorBase):
    def __init__(self, board):
        """Initialize the sensor."""
        super().__init__(board)

        self._attr_unique_id = f"{self._board.board_id}_link"

        # The name of the entity
        self._attr_name = f"{self._board.name} transaction link"
        self.entity_description = SensorEntityDescription(
            key="setpoint",
            name=self._attr_name,
        )

    @property
    def state(self):
        """Return the state of the sensor."""

        return self._board._link


class ToCompensate(SensorBase):
    def __init__(self, board):
        """Initialize the sensor."""
        super().__init__(board)

        self._attr_unique_id = f"{self._board.board_id}_to_compensate"

        # The name of the entity
        self._attr_name = f"{self._board.name} To Compensate"
        self.entity_description = SensorEntityDescription(
            key="setpoint",
            name=self._attr_name,
            native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
            device_class=DEVICE_CLASS_ENERGY,
            state_class=SensorStateClass.MEASUREMENT,
        )

    @property
    def state(self):
        """Return the state of the sensor."""

        return self._board._to_compensate


class TokensToBurn(SensorBase):
    def __init__(self, board):
        """Initialize the sensor."""
        super().__init__(board)

        self._attr_unique_id = f"{self._board.board_id}_tokens_to_burn"

        # The name of the entity
        self._attr_name = f"{self._board.name} Tokens"
        self.entity_description = SensorEntityDescription(
            key="setpoint",
            name=self._attr_name,
            state_class=SensorStateClass.MEASUREMENT,
        )

    @property
    def state(self):
        """Return the state of the sensor."""

        return self._board._tokens_to_burn
