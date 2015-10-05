//
//  UserModel.swift
//  SapphireDesign
//
//  Created by gxwang on 15/9/1.
//  Copyright (c) 2015年 sapphire. All rights reserved.
//

import Foundation
import Alamofire
import SwiftyJSON
import AFNetworking

class UserModel {
    var username:String = ""
    var account:String = ""
    var password:String = ""
    var usersex:String = ""
    var netheadimage:String = ""
    var islogined:Bool = false
    
    func login(account:String,pwd:String,block:((AnyObject)->())?)->Request {
        log.info("\(GlobalUrl.URL_LOGIN)")
        
        return Alamofire.request(.GET, GlobalUrl.URL_LOGIN, parameters: ["myUserPhone":account]).responseJSON() {
            (_,_,Result) in
            
            log.info("Alamofire Error is \(Result.error)")
            
            if Result.isFailure == true {
                block?(ERROR_CODE_ERROR_NETWORK)
                return
            }
            
            NSSearchPathForDirectoriesInDomains(.DocumentDirectory, .UserDomainMask, true)
            
            var json = JSON(Result.value!)
            log.info("\(json)")
            print("\(json)")
            var jsonPwd = json[0]["password"].stringValue
            if pwd != jsonPwd {
                block?(ERROR_CODE_ERROR_PWD)
                return
            }
            self.account =  account
            self.password = pwd
            self.setUserInfo(json[0])
            self.cacheUserImage(nil)
            block?(ERROR_CODE_NO_ERROR)
        }
    }
    
    //下载用户图像
    func cacheUserImage(block:(()->())?) {
        //判断用户图像是否存在，如果存在就不需要下载
        var userImagePath = GlobalDir.getUserImageCache(self.account)
        if GlobalDir.fileExistAtPath(userImagePath) == true {
            return
        }
        log.info(self.netheadimage)
        if self.netheadimage.isEmpty == false {
            var netUserImage = GlobalUrl.URL_GET_USER_IMAGE.URLByAppendingPathComponent(self.netheadimage)
            Alamofire.download(.GET, netUserImage) {
                (_,_) in
                var path = GlobalDir.userImageCacheURL(self.account)
                log.info("\(path)")
                return path
            }
        }
    }
    
    private func setUserInfo(json:JSON) {
        self.username = json["user_name"].stringValue
        self.usersex = json["sex"].stringValue
        self.netheadimage = json["head_image_url"].stringValue
        self.islogined = true
        
        NSUserDefaults.standardUserDefaults().setValue(self.account, forKey: LOGIN_ACCOUNT)
        NSUserDefaults.standardUserDefaults().setValue(self.password, forKey: LOGIN_PASSWORD)
        NSUserDefaults.standardUserDefaults().setBool(true, forKey: LOGIN_AUTO)
    }
    
    func loginOut() {
        self.islogined = false
        
        self.account = ""
        self.username = ""
        self.password = ""
        self.netheadimage = ""
        self.usersex = ""
    }
    
}