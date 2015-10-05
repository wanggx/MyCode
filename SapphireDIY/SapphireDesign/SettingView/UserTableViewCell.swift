//
//  UserTableViewCell.swift
//  SapphireDesign
//
//  Created by gxwang on 15/9/7.
//  Copyright (c) 2015年 sapphire. All rights reserved.
//

import Foundation
import UIKit

class UserTableViewCell : UITableViewCell {
    
    @IBOutlet weak var userHeadImageView: UIImageView!
    @IBOutlet weak var userNameLabel: UILabel!
    
    override func awakeFromNib() {
        super.awakeFromNib()
        NSNotificationCenter.defaultCenter().addObserver(self, selector: "initUserCell", name: LOGIN_SUCCESS, object: nil)
        log.info("awakeFromNib")
    }
    
    func initUserCell() {
        
        if GlobalVar.UserInfo.islogined == true {
            userNameLabel.text = "账号:" + GlobalVar.UserInfo.account
            let headImage = GlobalDir.getUserImageCache(GlobalVar.UserInfo.account)
            userHeadImageView.image = UIImage(named: "1_1.png")
        } else {
            userHeadImageView.image = UIImage(named: "1_1.png")
            userNameLabel.text = "你还未登陆"
        }
    }
    
    deinit {
        NSNotificationCenter.defaultCenter().removeObserver(self)
    }
    
}
