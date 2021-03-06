//
//  HeaderTabSegmentButton.swift
//  SapphireDesign
//
//  Created by 波 冯 on 15/8/24.
//  Copyright (c) 2015年 sapphire. All rights reserved.
//

import Foundation
import UIKit


class HeaderTabSegmentButton:UIButton
{
    override init(frame: CGRect)
    {
        super.init(frame: frame)
        self.setTitleColor(UIColor.darkGrayColor(), forState: UIControlState.Normal)
        self.setTitleColor(UIColor.darkTextColor(), forState: UIControlState.Selected)
        self.titleLabel?.textColor = UIColor.darkTextColor()
        self.backgroundColor = UIColor.clearColor()
    }
    
    required init?(coder aDecoder: NSCoder)
    {
        fatalError("init(coder:) has not been implemented")
    }
    
    override func touchesBegan(touches: Set<UITouch>, withEvent event: UIEvent?)
    {
        super.touchesBegan(touches, withEvent: event)
        self.backgroundColor = UIColor.clearColor()
    }
    
    override func touchesEnded(touches: Set<UITouch>, withEvent event: UIEvent?)
    {
        super.touchesEnded(touches, withEvent: event)
        self.backgroundColor = UIColor.clearColor()
    }

}