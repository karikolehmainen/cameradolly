//
//  MessageBroker.swift
//  CameraDolly
//
//  Created by Kari Kolehmainen on 13.12.2021.
//

import Foundation
import CocoaMQTT
import SwiftUI

enum MBAction {
    case connectToServer
}

class MBLink : ObservableObject {
    @Published var action : MBAction?
    
    func connectToServer() {
        action = .connectToServer
    }
}

class MessageBroker : ObservableObject {
    var client: String?
    var mqttVersion: String?
    var defaultHost = UserDefaults.standard.string(forKey: "mqttHost") ?? ""
    var username = UserDefaults.standard.string(forKey: "mqttUser") ?? ""
    var password = UserDefaults.standard.string(forKey: "mqttPass") ?? ""
        
    var mqtt: CocoaMQTT?
    var ctrl: ContentView!
    
    init()
    {
        let clientID = "DollyApp"
        print("MessageBroger: init")
        mqtt = CocoaMQTT(clientID: clientID, host: defaultHost, port: 1883)
        mqtt!.username = username
        mqtt!.password = password
        mqtt!.willMessage = CocoaMQTTMessage(topic: "/CameraDolly/lastwill", string: "dieout")
        mqtt!.keepAlive = 60
        mqtt!.delegate = self
    }
    func setCtrlView(object: ContentView)
    {
        ctrl = object
    }
    
    func connectToServer() -> Bool {
        //_ = mqtt!.connect()
        let ret = mqtt!.connect()
        print("MessageBroger: connectToServer: ",ret)
        //mqtt!.subscribe("/CameraDolly/#")
        return ret
    }
    
    func startDolly(){
        print("MassageBroker:startDolly")
        let topic = "/CameraDolly/start"
        let message = ""
        sendMessage(message:message, topic: topic)
    }
    func stopDolly(){
        print("MassageBroker:stopDolly")
        let topic = "/CameraDolly/stop"
        let message = ""
        sendMessage(message:message, topic: topic)
    }
    func rotateHead(operation: String){
        print("MassageBroker:rotateHead:"+operation)
        var topic = "/CameraDolly/head_off"
        let message = ""
        if (operation == "Start Rotate")
        {
            topic = "/CameraDolly/rotate"
        }
        sendMessage(message:message, topic: topic)
    }
    func rewindDolly(){
        print("MassageBroker:rewindDolly")
        let topic = "/CameraDolly/gotostart"
        let message = ""
        sendMessage(message:message, topic: topic)
    }
    func levelHead(){
        print("MassageBroker:levelHead")
        let topic = "/CameraDolly/level_horizon"
        let message = ""
        sendMessage(message:message, topic: topic)
    }
    func alignHead(){
        print("MassageBroker:alignHead")
        var locationManager = LocationManager()
        let location = locationManager.location
        let topic = "/CameraDolly/align_axis"
        var message = "79.95"
        if (location != nil)
        {
            message = String(location!.latitude)
        }
        sendMessage(message:message, topic: topic)
    }
    
    func setHostAddr(host: String){
        self.defaultHost = host
    }
    
    func setUsername(user: String){
        self.username = user
    }
    
    func setPassword(pass: String){
        self.password = pass
    }
    
    @IBAction func sendMessage(message: String, topic: String) {
        let publishProperties = MqttPublishProperties()
        publishProperties.contentType = "JSON"
        let ret = mqtt!.publish(topic, withString: message, qos: .qos1)
        print("MessageBroker senMessage: ", ret)
    }
    
    @IBAction func disconnect() {
        mqtt!.disconnect()
    }
    
    @objc func disconnectMessage(notification: NSNotification) {
        disconnect()
    }
    
    @objc func receivedMessage(notification: NSNotification) {
        let userInfo = notification.userInfo as! [String: AnyObject]
        let message = userInfo["message"] as! String
        let topic = userInfo["topic"] as! String
        print("MassageBroker:receivedMessage  "+message+","+topic+")")
        //messages.append(chatMessage)
    }
}

extension MessageBroker: CocoaMQTTDelegate {
    // Optional ssl CocoaMQTTDelegate
    func mqtt(_ mqtt: CocoaMQTT, didReceive trust: SecTrust, completionHandler: @escaping (Bool) -> Void) {
        TRACE("trust: \(trust)")
        /// Validate the server certificate
        ///
        /// Some custom validation...
        ///
        /// if validatePassed {
        ///     completionHandler(true)
        /// } else {
        ///     completionHandler(false)
        /// }
        completionHandler(true)
    }

    func mqtt(_ mqtt: CocoaMQTT, didConnectAck ack: CocoaMQTTConnAck) {
        TRACE("ack: \(ack)")

        if ack == .accept {
            print("MassageBroker:CocoaMQTTDelegate:mqtt subscribe to topics")
            mqtt.subscribe("/CameraDolly/#", qos: CocoaMQTTQoS.qos1)

            //let chatViewController = storyboard?.instantiateViewController(withIdentifier: "ChatViewController") as? ChatViewController
            //chatViewController?.mqtt = mqtt
            //chatViewController?.mqttVersion = mqttVesion
            //navigationController!.pushViewController(chatViewController!, animated: true)
        }
    }

    func mqtt(_ mqtt: CocoaMQTT, didStateChangeTo state: CocoaMQTTConnState) {
        TRACE("new state: \(state)")
    }

    func mqtt(_ mqtt: CocoaMQTT, didPublishMessage message: CocoaMQTTMessage, id: UInt16) {
        TRACE("message: \(message.string.description), id: \(id)")
    }

    func mqtt(_ mqtt: CocoaMQTT, didPublishAck id: UInt16) {
        TRACE("id: \(id)")
    }

    func mqtt(_ mqtt: CocoaMQTT, didReceiveMessage message: CocoaMQTTMessage, id: UInt16 ) {
        TRACE("message: \(message.string.description), id: \(id)")
        if (message.topic == "/CameraDolly/StatusMessage")
        {
            ctrl.updateState(message: message.string ?? "")
        }
        //ctrl.stateToUpdate = message.string ?? ""
        let name = NSNotification.Name(rawValue: "MQTTMessageNotification")
        NotificationCenter.default.post(name: name, object: self, userInfo: ["message": message.string!, "topic": message.topic, "id": id])
    }

    func mqtt(_ mqtt: CocoaMQTT, didSubscribeTopics success: NSDictionary, failed: [String]) {
        TRACE("subscribed: \(success), failed: \(failed)")
    }

    func mqtt(_ mqtt: CocoaMQTT, didUnsubscribeTopics topics: [String]) {
        TRACE("topic: \(topics)")
    }

    func mqttDidPing(_ mqtt: CocoaMQTT) {
        TRACE()
    }

    func mqttDidReceivePong(_ mqtt: CocoaMQTT) {
        TRACE()
    }

    func mqttDidDisconnect(_ mqtt: CocoaMQTT, withError err: Error?) {
        TRACE("\(err.description)")
    }
}

extension MessageBroker {
    func TRACE(_ message: String = "", fun: String = #function) {
        let names = fun.components(separatedBy: ":")
        var prettyName: String
        if names.count == 2 {
            prettyName = names[0]
        } else {
            prettyName = names[1]
        }
        
        if fun == "mqttDidDisconnect(_:withError:)" {
            prettyName = "didDisconnect"
        }

        print("[TRACE] [\(prettyName)]: \(message)")
    }
}

extension Optional {
    // Unwrap optional value for printing log only
    var description: String {
        if let self = self {
            return "\(self)"
        }
        return ""
    }
}
