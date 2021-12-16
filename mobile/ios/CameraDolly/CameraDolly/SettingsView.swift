//
//  SettingsView.swift
//  CameraDolly
//
//  Created by Kari Kolehmainen on 13.12.2021.
//

import SwiftUI

struct SettingsView: View {
    @State private var mqttHost = UserDefaults.standard.string(forKey: "mqttHost") ?? ""
    @State private var mqttUser = UserDefaults.standard.string(forKey: "mqttUser") ?? ""
    @State private var mqttPass = UserDefaults.standard.string(forKey: "mqttPass") ?? ""
    
    var body: some View {
        let bindingHost = Binding<String>(get: {
            self.mqttHost
                }, set: {
                    self.mqttHost = $0
                    print("mqtt host field chnged") // You can do anything due to the change here.
                    UserDefaults.standard.set(self.mqttHost, forKey: "mqttHost")
                })
        let bindingUser = Binding<String>(get: {
            self.mqttUser
                }, set: {
                    self.mqttUser = $0
                    print("mqtt user field chnged") // You can do anything due to the change here.
                    UserDefaults.standard.set(self.mqttUser, forKey: "mqttUser")
                })
        let bindingPass = Binding<String>(get: {
            self.mqttPass
                }, set: {
                    self.mqttPass = $0
                    print("mqtt pass field chnged") // You can do anything due to the change here.
                    UserDefaults.standard.set(self.mqttPass, forKey: "mqttPass")
                })
        VStack {
            Text("Change Dolly Settings")
            TextField("MQTT Host Address", text: bindingHost)
                .padding(2.0)
                .overlay(RoundedRectangle(cornerRadius: 3.0).stroke(lineWidth: 2.0))
            TextField("Username", text: bindingUser).padding(2.0)
                .overlay(RoundedRectangle(cornerRadius: 3.0).stroke(lineWidth: 2.0))
            TextField("Password", text: bindingPass).padding(2.0)
                .overlay(RoundedRectangle(cornerRadius: 3.0).stroke(lineWidth: 2.0))
            Spacer()
        }.padding(10.0)
    }
}

struct SettingsView_Previews: PreviewProvider {
    static var previews: some View {
        SettingsView()
    }
}
