//
//  LoginViewController.swift
//  SapphireDesign
//
//  Created by 冯 波 on 15/8/21.
//  Copyright (c) 2015年 sapphire. All rights reserved.
//

import Foundation
import UIKit
import Alamofire
import ReactiveCocoa

class LoginViewController:UIViewController
{
    //prototype
    @IBOutlet weak var userNameTextField: MadokaTextField!
    @IBOutlet weak var passwordTextField: MadokaTextField!
    @IBOutlet weak var loginButton: UIButton!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        passwordTextField.secureTextEntry = true
        initSignal()
    }
    
    func initSignal() {
        let usernameSingal = userNameTextField.rac_textSignal().map {
            (text) in return self.isVaildUserName(text as! String)
        }
        
        let vaildpwdSingal = passwordTextField.rac_textSignal().map() {
            (text) in return self.isValidPwd(text as! String)
        }
        
        let signupActiveSignal =  RACSignal.combineLatest([usernameSingal, vaildpwdSingal]).map {
            let tuple = $0 as! RACTuple
            let bools: [Bool] = tuple.allObjects() as! [Bool]
            let result: Bool = bools.reduce(true) {$0 && $1}
            return result
        }
        signupActiveSignal ~> RAC(self.loginButton, "enabled")
        
        loginButton.rac_signalForControlEvents(UIControlEvents.TouchUpInside)
            .doNext {
                _ in
                self.loginButton.enabled = false
            }
            .flattenMap(signInSignal)
            .subscribeNext {
                let code = $0 as! Int
                self.loginButton.enabled = true
                if code == ERROR_CODE_NO_ERROR {
                    self.loginSuccess()
                } else {
                    processErrorCode(code)
                }
        }
    }
    

    func isValidPwd(pwd:String)->Bool {
        if pwd.characters.count >= 6 {
            return true
        }
        return false
    }
    
    func isVaildUserName(name:String)->Bool {
        if name.characters.count < 3 {
            return false
        }
        return true
    }
    
    override func didReceiveMemoryWarning()
    {
        super.didReceiveMemoryWarning()
    }
    
    func loginSuccess() {
        self.dismissViewControllerAnimated(true, completion: nil)
    }
    
    func signInSignal(_ : AnyObject!) -> RACSignal {
        return RACSignal.createSignal {
            subscriber in
            GlobalVar.UserInfo.login(self.userNameTextField.text!, pwd: self.passwordTextField.text!) { (code) in
                subscriber.sendNext(code)
                subscriber.sendCompleted()
            }
            return nil
        }
    }
    
    @IBAction func backBtnClicked(sender: AnyObject) {
        
        self.dismissViewControllerAnimated(true, completion: nil)
    }
    
    
    override func observeValueForKeyPath(keyPath: String?, ofObject object: AnyObject?, change: [String : AnyObject]?, context: UnsafeMutablePointer<Void>) {
    }
}
