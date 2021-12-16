//
//  MainView.swift
//  CameraDolly
//
//  Created by Kari Kolehmainen on 13.12.2021.
//

import SwiftUI

struct MainView: View {

    //@ObservedObject var messagebroker = MessageBroker()
   //@State var messagebroker = MessageBroker()
    let messagebroker: MessageBroker
    //let barFunc: (()->Int)
    
    init() {
        messagebroker = MessageBroker()
        messagebroker.connectToServer()
    }
    
    var body: some View {
        TabView {
            //ContentView(broker: self.$messagebroker)
            ContentView(brkr_ptr: self.messagebroker)
                .tabItem {
                    Label("Control", systemImage: "list.dash")
                }
            CameraView()
                .tabItem {
                    Label("Camera", systemImage: "camera.dash")
                }
            SettingsView()
                .tabItem {
                    Label("Settings", systemImage: "list.dash")
                }
        }
    }
}

struct MainView_Previews: PreviewProvider {
    static var previews: some View {
        MainView()
    }
}
