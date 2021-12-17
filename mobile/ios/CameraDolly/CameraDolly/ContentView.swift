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
    @ObservedObject var viewModel: ExternalModel = ExternalModel()
    let decoder = JSONDecoder()
    
    init(brkr_ptr: MessageBroker)
    {
        broker = brkr_ptr
       
        broker.setCtrlView(object: self)
    }
    
    var body: some View {
        var ret = 0
        VStack {
            HStack {
                Text(viewModel.statusToUpdate)
                Text("Control Dolly")
                    .padding()
            }
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
                    }
                    .padding(10.0)
                    .overlay(RoundedRectangle(cornerRadius: 10.0).stroke(lineWidth: 2.0))
                    

                }
            }
            HStack {
                Button(action: {
                    broker.levelHead()
                    print("level camera head")
                }) {
                    HStack {
                        Image(systemName: "level.fill")
                        Text("Level")
                    }.padding(10.0)
                        .overlay(RoundedRectangle(cornerRadius: 10.0).stroke(lineWidth: 2.0))
                }
                Button(action: {
                    broker.alignHead()
                    print("Align head with Earth axis")
                }) {
                    HStack {
                        Image(systemName: "align.fill")
                        Text("Align")
                    }.padding(10.0)
                        .overlay(RoundedRectangle(cornerRadius: 10.0).stroke(lineWidth: 2.0))
                }
                Button(action: {
                    broker.rotateHead(operation: viewModel.headRotate)
                    print("rotate camera head")
                }) {
                    HStack {
                        Image(systemName: "rotate.fill")
                        Text(viewModel.headRotate)
                    }.padding(10.0)
                        .overlay(RoundedRectangle(cornerRadius: 10.0).stroke(lineWidth: 2.0))
                }
            }
            Spacer()
            HStack {
                Text("Position:")
                Text(viewModel.dollyPosition)
            }
            Spacer()
            Text(viewModel.stateToUpdate)
        }
    }
    func updateState(message: String)
    {
        print("ContentView:updateState:"+message)
        viewModel.stateToUpdate = message
        do{
            let status = try decoder.decode(DollyStatus.self, from: message.data(using: .utf8)!)
            if (status.running == 1) {
                viewModel.statusToUpdate = "RUN"
            }
            else {
                viewModel.statusToUpdate = "STOP"
            }
            if (status.head_status == 1) {
                viewModel.headRotate = "Stop Rotate"
            }
            else {
                viewModel.headRotate = "Start Rotate"
            }
            viewModel.dollyPosition = String(format: "%.2f", status.position)
        }
        catch {
            print("JSON error")
        }
    }
}

class ExternalModel: ObservableObject {
    @Published var stateToUpdate: String = "state"
    @Published var statusToUpdate: String = "status"
    @Published var headRotate: String = "Start Rotate"
    @Published var dollyPosition: String = "--??--"

    func registerRequest() {
        // other functionality
        stateToUpdate = "I've been updated!"
    }
}

struct DollyStatus: Codable {
    var heading: Double
    var running: Int
    var head_status: Int
    var position: Double
}
