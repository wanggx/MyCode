//
//  SettingTableViewCell.swift
//  SapphireDesign
//
//  Created by gxwang on 15/9/7.
//  Copyright (c) 2015年 sapphire. All rights reserved.
//

import Foundation
import UIKit


class SettingTableViewCell : UITableViewCell {
    
    
    func initViewCell(index:NSIndexPath) {
        self.imageView?.image = UIImage(named: "1_1.png")
        self.textLabel?.text = "设置"
        if index.section == 1 {
            if index.row == 0 {
                self.textLabel?.text = "我的订单"
            } else if index.row == 1 {
                self.textLabel?.text = "我的购物车"
            }
        } else if index.section == 2 {
            if index.row == 0 {
                self.textLabel?.text = "我的消息"
            } else {
                self.textLabel?.text = "我的DIY"
            }
        }
    }
}
