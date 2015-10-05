//
//  HeaderTabSegmentView.swift
//  SapphireDesign
//
//  Created by 波 冯 on 15/8/24.
//  Copyright (c) 2015年 sapphire. All rights reserved.
//

import Foundation
import UIKit


class HeaderTabSegmentView : UIView {
    
    
    var btnFinishedOrder : HeaderTabSegmentButton!
    var btnNonFinishOrder: HeaderTabSegmentButton!
    
    var headerLineView:UIView!
    
    var startx:CGFloat!
    var starty:CGFloat!
    var buttonWidth:CGFloat!
    var buttonHeight:CGFloat!
    
    var scrollView:UIScrollView!
    
    override init(frame: CGRect) {
        super.init(frame: frame)
        
        self.backgroundColor = UIColor(red: 0.9, green: 0.9, blue: 0.9, alpha: 0.5)
        
        startx = self.frame.width / 8
        buttonWidth  = (self.frame.width - self.frame.width * 2 / 8) / 2 //has been changed
        buttonHeight = (self.frame.height - 4) * 0.6
        starty = (self.frame.height - 4) * 0.4
        
        headerLineView = UIView(frame: CGRectMake(startx, self.frame.height - 5, buttonWidth, 3))
        headerLineView.backgroundColor = UIColor(red: 0.2, green: 0.4, blue: 0.5, alpha: 0.8)
        headerLineView.layer.cornerRadius = 1
        self.addSubview(headerLineView)
        
        
        btnNonFinishOrder = HeaderTabSegmentButton(frame: CGRectMake(startx, starty, buttonWidth, buttonHeight))
        btnNonFinishOrder.tag = 0
        btnNonFinishOrder.setTitle("热门", forState: UIControlState.Normal)
        btnNonFinishOrder.addTarget(self, action: Selector("headerClick:"), forControlEvents: UIControlEvents.TouchUpInside)
        btnNonFinishOrder.selected = true //默认选择第一个

        
        btnFinishedOrder = HeaderTabSegmentButton(frame: CGRectMake(startx + buttonWidth, starty, buttonWidth, buttonHeight))
        btnFinishedOrder.tag = 1
        btnFinishedOrder.setTitle("素材", forState: UIControlState.Normal)
        btnFinishedOrder.addTarget(self, action: Selector("headerClick:"), forControlEvents: UIControlEvents.TouchUpInside)
        
        
        self.addSubview(btnFinishedOrder)
        self.addSubview(btnNonFinishOrder)
    }
    
    func headerClick(sender:HeaderTabSegmentButton)
    {
        modifyButtonSelect(sender.tag)
        var frame = scrollView.frame
        frame.origin.x = frame.size.width * CGFloat(sender.tag)
        frame.origin.y = 0
        scrollView.scrollRectToVisible(frame, animated:true)
    }
    
    func modifyButtonSelect(index:Int)
    {
        btnFinishedOrder.selected = false
        btnNonFinishOrder.selected = false
        
        if(index == 0)
        {
            btnNonFinishOrder.selected = true
        }
        else if(index == 1)
        {
            btnFinishedOrder.selected = true
        }
        
        headerLineViewAnimate(index)
    }
    
    func headerLineViewAnimate(targetIndex:Int)
    {
        
        UIView.animateWithDuration(0.3, animations: {
            
            self.headerLineView.frame = CGRectMake(self.startx + self.buttonWidth*CGFloat(targetIndex), self.frame.height - 5, self.buttonWidth, 3)
            }, completion: {_ in
                
        })
        
    }
    
    required init?(coder aDecoder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
}

