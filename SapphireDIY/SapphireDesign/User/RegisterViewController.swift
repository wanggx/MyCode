//
//  RegisterViewController.swift
//  SapphireDesign
//
//  Created by gxwang on 15/9/7.
//  Copyright (c) 2015年 sapphire. All rights reserved.
//

import Foundation
import UIKit

class RegisterViewController : UIViewController {
    
    override func viewDidLoad() {
        super.viewDidLoad()
    }
    
    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
    }
    
    @IBAction func doneBtnClicked(sender: AnyObject) {
        self.dismissViewControllerAnimated(true, completion: nil)
    }
}
