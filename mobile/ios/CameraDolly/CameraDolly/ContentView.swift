//
//  ContentView.swift
//  CameraDolly
//
//  Created by Kari Kolehmainen on 13.12.2021.
//

import SwiftUI

struct ContentView: View {
    //@Binding var broker: MessageBroker
    var broker: MessageBroker
    
    init(brkr_ptr: MessageBroker)
    {
        broker = brkr_ptr
    }
    
    var body: some View {
        var ret = 0
        VStack {
            Text("Control Dolly")
                .padding()
            HStack {
                Button(action: {
                    broker.startDolly()
                    print("Start Dolly")
                }) {
                    HStack {
                        Image(systemName: "play.fill")
                        Text("Start")
                    }.padding(10.0)
                        .overlay(RoundedRectangle(cornerRadius: 10.0).stroke(lineWidth: 2.0))
                }
                Button(action: {
                    broker.stopDolly()
                    print("Stop Dolly")
                }) {
                    HStack {
                        Image(systemName: "stop.fill")
                        Text("Stop")
                    }.padding(10.0)
                        .overlay(RoundedRectangle(cornerRadius: 10.0).stroke(lineWidth: 2.0))
                }
                Button(action: {
                    broker.rewindDolly()
                    print("Return to start")
                }) {
                    HStack {
                        Image(systemName: "rewind.fill")
                        Text("Return")
                    }.padding(10.0)
                        .overlay(RoundedRectangle(cornerRadius: 10.0).stroke(lineWidth: 2.0))
                }
            }
            Spacer()
        }
    }
}

//struct ContentView_Previews: PreviewProvider {
    //static var previews: some View {
        //ContentView()
    //}
//}
