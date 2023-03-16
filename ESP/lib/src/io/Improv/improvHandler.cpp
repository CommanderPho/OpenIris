#include "improvHandler.hpp"

ImprovHandler::ImprovHandler(ProjectConfig* projectConfig,
                             StateManager<WiFiState_e>* wifiStateManager,
                             StateManager<LEDStates_e>* stateManager)
    : projectConfig(projectConfig), _buffer{0}, _position(0) {}

ImprovHandler::~ImprovHandler() {
  if (_buffer)
    free(_buffer);
}

void ImprovHandler::onErrorCallback(improv::Error err) {
  stateManager->setState(LEDStates_e::_Improv_Error);
}

bool ImprovHandler::onCommandCallback(improv::ImprovCommand cmd) {
  switch (cmd.command) {
    case improv::Command::GET_CURRENT_STATE: {
      auto wifiConfigs = projectConfig->getWifiConfigs();
      if (wifiConfigs->size() == 0) {
        this->set_state(improv::State::STATE_AUTHORIZED);
      } else {
        this->set_state(improv::State::STATE_PROVISIONED);
      }
      break;
    }

    case improv::Command::WIFI_SETTINGS: {
      auto mdnsConfig = projectConfig->getMDNSConfig();
      stateManager->setState(LEDStates_e::_Improv_Start);

      projectConfig->setWifiConfig(cmd.ssid, cmd.ssid, cmd.password, 10, 52,
                                   false, true);
      set_state(improv::STATE_PROVISIONING);

      set_state(improv::STATE_PROVISIONED);

      stateManager->setState(LEDStates_e::_Improv_Processing);
      // construct url
      std::string root_url = "http://" + mdnsConfig->hostname + ".local";
      std::vector<std::string> url = {root_url};
      std::vector<uint8_t> data =
          improv::build_rpc_response(improv::WIFI_SETTINGS, url, false);
      this->send_response(data);
      //* Save the config to flash
      projectConfig->wifiConfigSave();
      stateManager->setState(LEDStates_e::_Improv_Stop);
      break;
    }

    case improv::Command::GET_DEVICE_INFO: {
      std::vector<std::string> infos = {"OpenIris", VERSION, CAMERA_MODULE_NAME,
                                        "EyeTrackVR"};
      std::vector<uint8_t> data =
          improv::build_rpc_response(improv::GET_DEVICE_INFO, infos, false);
      this->send_response(data);
      break;
    }

    case improv::Command::GET_WIFI_NETWORKS: {
      this->getNetworks();
      break;
    }

    default: {
      this->set_error(improv::ERROR_UNKNOWN_RPC);
      return false;
    }
  }

  return true;
}

void ImprovHandler::getNetworks() {
  if (wifiStateManager->getCurrentState() == WiFiState_e::WiFiState_ADHOC) {
    Network_Utilities::setupWifiScan();
  }
  int networkNum = WiFi.scanNetworks(true, true);
  for (int id = 0; id < networkNum; ++id) {
    std::vector<uint8_t> data = improv::build_rpc_response(
        improv::GET_WIFI_NETWORKS,
        {WiFi.SSID(id), String(WiFi.RSSI(id)),
         (WiFi.encryptionType(id) == WIFI_AUTH_OPEN ? "NO" : "YES")},
        false);
    this->send_response(data);
    Network_Utilities::my_delay(0.01);
  }
  // final response
  std::vector<uint8_t> data = improv::build_rpc_response(
      improv::GET_WIFI_NETWORKS, std::vector<std::string>{}, false);
  this->send_response(data);
}

void ImprovHandler::set_state(improv::State state) {
  std::vector<uint8_t> data = {'I', 'M', 'P', 'R', 'O', 'V'};
  data.resize(11);
  data[6] = improv::IMPROV_SERIAL_VERSION;
  data[7] = improv::TYPE_CURRENT_STATE;
  data[8] = 1;
  data[9] = state;

  uint8_t checksum = 0x00;
  for (uint8_t d : data)
    checksum += d;
  data[10] = checksum;

  Serial.write(data.data(), data.size());
}

void ImprovHandler::send_response(std::vector<uint8_t>& response) {
  std::vector<uint8_t> data = {'I', 'M', 'P', 'R', 'O', 'V'};
  data.resize(9);
  data[6] = improv::IMPROV_SERIAL_VERSION;
  data[7] = improv::TYPE_RPC_RESPONSE;
  data[8] = response.size();
  data.insert(data.end(), response.begin(), response.end());

  uint8_t checksum = 0x00;
  for (uint8_t d : data)
    checksum += d;
  data.push_back(checksum);

  Serial.write(data.data(), data.size());
}

void ImprovHandler::set_error(improv::Error error) {
  std::vector<uint8_t> data = {'I', 'M', 'P', 'R', 'O', 'V'};
  data.resize(11);
  data[6] = improv::IMPROV_SERIAL_VERSION;
  data[7] = improv::TYPE_ERROR_STATE;
  data[8] = 1;
  data[9] = error;

  uint8_t checksum = 0x00;
  for (uint8_t d : data)
    checksum += d;
  data[10] = checksum;

  Serial.write(data.data(), data.size());
}

void ImprovHandler::loop() {
  if (Serial.available() > 0) {
    uint8_t b = Serial.read();
    bool valid = improv::parse_improv_serial_byte(
        _position, b, _buffer,
        [&](improv::ImprovCommand cmd) -> bool {
          return this->onCommandCallback(cmd);
        },
        [&](improv::Error error) { this->onErrorCallback(error); });

    if (valid) {
      _buffer[_position++] = b;
      return;
    }
    _position = 0;
  }
}

void ImprovHandler::update(ObserverEvent::Event event) {
  /* switch (event) {
    case ObserverEvent::Event::WIFI_CONNECTED:
      set_state(improv::STATE_AUTHORIZED);
      break;
    case ObserverEvent::Event::WIFI_DISCONNECTED:
      set_state(improv::STATE_PROVISIONED);
      break;
    default:
      break;
  } */
}
