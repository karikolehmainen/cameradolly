//
//  MessageBroker.swift
//  CameraDolly
//
//  Created by Kari Kolehmainen on 13.12.2021.
//

import Foundation
import CocoaMQTT


class MessageBroker {
    var client: String?
    var mqttVersion: String?
    let defaultHost = "broker-cn.emqx.io"
        
    var mqtt5: CocoaMQTT5?
    var mqtt: CocoaMQTT?
    var animal: String?
    var mqttVesion: String?
    
    
    @IBAction func connectToServer() {
            if mqttVesion == "3.1.1" {
                _ = mqtt!.connect()
            }else if mqttVesion == "5.0"{
                _ = mqtt5!.connect()
            }

        }

    func sendAuthToServer(){
            let authProperties = MqttAuthProperties()
            mqtt5!.auth(reasonCode: CocoaMQTTAUTHReasonCode.continueAuthentication, authProperties: authProperties)
        }
    
    func mqttSettingList(){
            mqttSetting()
            //selfSignedSSLSetting()
            //simpleSSLSetting()
            //mqttWebsocketsSetting()
            //mqttWebsocketSSLSetting()
        }


    func mqttSetting() {
        if mqttVesion == "3.1.1" {
            let clientID = "CocoaMQTT-\(animal!)-" + String(ProcessInfo().processIdentifier)
            mqtt = CocoaMQTT(clientID: clientID, host: defaultHost, port: 1883)
            //mqtt!.logLevel = .debug
            mqtt!.username = ""
            mqtt!.password = ""
            mqtt!.willMessage = CocoaMQTTMessage(topic: "/will", string: "dieout")
            mqtt!.keepAlive = 60
            mqtt!.delegate = self
            //mqtt!.autoReconnect = true
                
        }else if mqttVesion == "5.0" {
            let clientID = "CocoaMQTT5-\(animal!)-" + String(ProcessInfo().processIdentifier)
            mqtt5 = CocoaMQTT5(clientID: clientID, host: defaultHost, port: 1883)
            //mqtt5!.logLevel = .debug
            let connectProperties = MqttConnectProperties()
            connectProperties.topicAliasMaximum = 0
            connectProperties.sessionExpiryInterval = 0
            connectProperties.receiveMaximum = 100
            connectProperties.maximumPacketSize = 500

            mqtt5!.connectProperties = connectProperties
            mqtt5!.username = ""
            mqtt5!.password = ""

            let lastWillMessage = CocoaMQTT5Message(topic: "/chat/room/animals/client/Sheep", string: "dieout")
            lastWillMessage.contentType = "JSON"
            lastWillMessage.willResponseTopic = "/chat/room/animals/client/Sheep"
            lastWillMessage.willExpiryInterval = 0
            lastWillMessage.willDelayInterval = 0
            lastWillMessage.qos = .qos1

            mqtt5!.willMessage = lastWillMessage
            mqtt5!.keepAlive = 60
            mqtt5!.delegate = self
            //mqtt5!.autoReconnect = true
        }

    }
    
    @IBAction func sendMessage(message: String) {
        let publishProperties = MqttPublishProperties()
        publishProperties.contentType = "JSON"

        if mqttVersion == "3.1.1" {
            mqtt!.publish("chat/room/animals/client/" + animal!, withString: message, qos: .qos1)
        }else if mqttVersion == "5.0" {
            mqtt5!.publish("chat/room/animals/client/" + animal!, withString: message, qos: .qos1, DUP: false, retained: false, properties: publishProperties)
        }
    }
    
    @IBAction func disconnect() {
        if mqttVersion == "3.1.1" {
            mqtt!.disconnect()
        }else if mqttVersion == "5.0" {
            mqtt5!.disconnect()
        }
    }
    
    @objc func disconnectMessage(notification: NSNotification) {
        disconnect()
    }
    
    @objc func receivedMessage(notification: NSNotification) {
        let userInfo = notification.userInfo as! [String: AnyObject]
        let content = userInfo["message"] as! String
        let topic = userInfo["topic"] as! String
        let id = UInt16(userInfo["id"] as! UInt16)
        let sender = topic.replacingOccurrences(of: "chat/room/animals/client/", with: "")
        //let chatMessage = ChatMessage(sender: sender, content: content, id: id)
        //messages.append(chatMessage)
    }

    @objc func receivedMqtt5Message(notification: NSNotification) {
        let userInfo = notification.userInfo as! [String: AnyObject]
        let message = userInfo["message"] as! String
        let topic = userInfo["topic"] as! String
        let id = UInt16(userInfo["id"] as! UInt16)
        //let sender = userInfo["animal"] as! String
        let sender = topic.replacingOccurrences(of: "chat/room/animals/client/", with: "")
        let content = String(message.filter { !"\0".contains($0) })
        //let chatMessage = ChatMessage(sender: sender, content: content, id: id)
        print("sendersendersender =  \(sender)")
        //messages.append(chatMessage)
    }
}

extension MessageBroker: CocoaMQTT5Delegate {
    
    func mqtt5(_ mqtt5: CocoaMQTT5, didReceiveDisconnectReasonCode reasonCode: CocoaMQTTDISCONNECTReasonCode) {
        print("disconnect res : \(reasonCode)")
    }
    
    func mqtt5(_ mqtt5: CocoaMQTT5, didReceiveAuthReasonCode reasonCode: CocoaMQTTAUTHReasonCode) {
        print("auth res : \(reasonCode)")
    }
    
    // Optional ssl CocoaMQTT5Delegate
    func mqtt5(_ mqtt5: CocoaMQTT5, didReceive trust: SecTrust, completionHandler: @escaping (Bool) -> Void) {
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
    
    func mqtt5(_ mqtt5: CocoaMQTT5, didConnectAck ack: CocoaMQTTCONNACKReasonCode, connAckData: MqttDecodeConnAck) {
        TRACE("ack: \(ack)")

        if ack == .success {
            print("properties maximumPacketSize: \(String(describing: connAckData.maximumPacketSize))")
            print("properties topicAliasMaximum: \(String(describing: connAckData.topicAliasMaximum))")
            
            mqtt5.subscribe("chat/room/animals/client/+", qos: CocoaMQTTQoS.qos1)
            //or
            //let subscriptions : [MqttSubscription] = [MqttSubscription(topic: "chat/room/animals/client/+"),MqttSubscription(topic: "chat/room/foods/client/+"),MqttSubscription(topic: "chat/room/trees/client/+")]
            //mqtt.subscribe(subscriptions)
            //let chatViewController = storyboard?.instantiateViewController(withIdentifier: "ChatViewController") as? ChatViewController
            //chatViewController?.mqtt5 = mqtt5
            //chatViewController?.mqttVersion = mqttVesion
            //navigationController!.pushViewController(chatViewController!, animated: true)
        }
    }
    
    func mqtt5(_ mqtt5: CocoaMQTT5, didStateChangeTo state: CocoaMQTTConnState) {
        TRACE("new state: \(state)")
        if state == .disconnected {

        }
    }
    
    func mqtt5(_ mqtt5: CocoaMQTT5, didPublishMessage message: CocoaMQTT5Message, id: UInt16) {
        TRACE("message: \(message.description), id: \(id)")
    }
    
    func mqtt5(_ mqtt5: CocoaMQTT5, didPublishAck id: UInt16, pubAckData: MqttDecodePubAck) {
        TRACE("id: \(id)")
        print("pubAckData reasonCode: \(String(describing: pubAckData.reasonCode))")
    }

    func mqtt5(_ mqtt5: CocoaMQTT5, didPublishRec id: UInt16, pubRecData: MqttDecodePubRec) {
        TRACE("id: \(id)")
        print("pubRecData reasonCode: \(String(describing: pubRecData.reasonCode))")
    }

    func mqtt5(_ mqtt5: CocoaMQTT5, didPublishComplete id: UInt16,  pubCompData: MqttDecodePubComp){
        TRACE("id: \(id)")
        print("pubCompData reasonCode: \(String(describing: pubCompData.reasonCode))")
    }

    func mqtt5(_ mqtt5: CocoaMQTT5, didReceiveMessage message: CocoaMQTT5Message, id: UInt16, publishData: MqttDecodePublish){
        print("publish.contentType \(String(describing: publishData.contentType))")
        
        TRACE("message: \(message.string.description), id: \(id)")
        let name = NSNotification.Name(rawValue: "MQTTMessageNotification" + animal!)

        NotificationCenter.default.post(name: name, object: self, userInfo: ["message": message.string!, "topic": message.topic, "id": id, "animal": animal as Any])
    }
    
    func mqtt5(_ mqtt5: CocoaMQTT5, didSubscribeTopics success: NSDictionary, failed: [String], subAckData: MqttDecodeSubAck) {
        TRACE("subscribed: \(success), failed: \(failed)")
        print("subAckData.reasonCodes \(String(describing: subAckData.reasonCodes))")
    }
    
    func mqtt5(_ mqtt5: CocoaMQTT5, didUnsubscribeTopics topics: [String], UnsubAckData: MqttDecodeUnsubAck) {
        TRACE("topic: \(topics)")
        print("UnsubAckData.reasonCodes \(String(describing: UnsubAckData.reasonCodes))")
        print("----------------------")
    }
    
    func mqtt5DidPing(_ mqtt5: CocoaMQTT5) {
        TRACE()
    }
    
    func mqtt5DidReceivePong(_ mqtt5: CocoaMQTT5) {
        TRACE()
    }

    func mqtt5DidDisconnect(_ mqtt5: CocoaMQTT5, withError err: Error?) {
        TRACE("\(err.description)")
        let name = NSNotification.Name(rawValue: "MQTTMessageNotificationDisconnect")
        NotificationCenter.default.post(name: name, object: nil)
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
            mqtt.subscribe("chat/room/animals/client/+", qos: CocoaMQTTQoS.qos1)

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

        let name = NSNotification.Name(rawValue: "MQTTMessageNotification" + animal!)
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
