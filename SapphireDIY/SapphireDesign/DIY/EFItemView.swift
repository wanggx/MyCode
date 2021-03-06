//
//  EFItemView.swift
//  SapphireDesign
//
//  Created by 波 冯 on 15/9/2.
//  Copyright (c) 2015年 sapphire. All rights reserved.
//

import Foundation
import UIKit

class EFItemView:UIButton{
    
    //init the delegate
    var delegate:EFItemViewDelegate!
    
    //basic parameter of the EFItemView
    var normal_:String!
    var highlighted_:String!
    var tag_:Int!
    var title:String!
    
    
    func initWithNormalImage(_normal:String,_highlighted:String,_tag:Int,_title:String)
    {
        
        self.normal_       = _normal
        self.highlighted_  = _highlighted
        self.tag_  = _tag
        self.title = _title
        
        configViews()
        
        
    }
    
    func configViews()
    {
        
        self.tag = tag_
        self.setBackgroundImage(UIImage(named: normal_), forState: UIControlState.Normal)
        self.setBackgroundImage(UIImage(named: highlighted_), forState: UIControlState.Highlighted)
        self.addTarget(self, action: Selector("btnTapped:"), forControlEvents: UIControlEvents.TouchUpInside)
        self.setTitle(title, forState: UIControlState.Normal)
        self.setTitleColor(UIColor.blackColor(), forState: UIControlState.Normal)
        self.titleLabel?.font = UIFont.systemFontOfSize(30)
    }
    
    func btnTapped(sender:UIButton)
    {
        print("the sender tag is \(sender.tag)")
        self.delegate.didTapped(sender.tag)
    }
    
}