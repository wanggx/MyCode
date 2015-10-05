//
//  GlobalFunc.swift
//  SapphireDesign
//
//  Created by gxwang on 15/9/8.
//  Copyright (c) 2015年 sapphire. All rights reserved.
//

import Foundation

class GlobalFunc {
    
    class func autoLogin()->Bool {
        
        var userName:String?
        var userPwd:String?
        var autoFlag = NSUserDefaults.standardUserDefaults().boolForKey(LOGIN_AUTO)
        if autoFlag == true {
            userName = NSUserDefaults.standardUserDefaults().stringForKey(LOGIN_ACCOUNT)
            userPwd = NSUserDefaults.standardUserDefaults().stringForKey(LOGIN_PASSWORD)
            
            if userName == nil || userPwd == nil {
                return false
            }
            
            dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0)) {
                GlobalVar.UserInfo.login(userName!, pwd: userPwd!) {
                    (code) in
                    var ret = code as! Int
                    if ret == ERROR_CODE_NO_ERROR {
                        NSNotificationCenter.defaultCenter().postNotificationName(LOGIN_SUCCESS, object: nil)
                    }
                }
            }
            return true
        }
        return false
    }
}