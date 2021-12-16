//
//  DollyViewController.swift
//  CameraDolly
//
//  Created by Kari Kolehmainen on 14.12.2021.
//

import Foundation
import UIKit
import SwiftUI

class DollyViewController: UIViewController {

    @IBSegueAction func showDetails(_ coder: NSCoder) -> UIViewController? {
        let mainView = MainView()
        return UIHostingController(coder: coder, rootView: mainView)
    }

    override func viewDidLoad() {
        super.viewDidLoad()

        // some code

    }
}
