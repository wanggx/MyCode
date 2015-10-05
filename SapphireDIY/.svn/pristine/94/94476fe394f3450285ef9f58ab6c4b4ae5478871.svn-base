//
//  DIYViewTemplate.swift
//  SapphireDesign
//
//  Created by 冯 波 on 15/9/13.
//  Copyright (c) 2015年 sapphire. All rights reserved.
//

import UIKit
import Foundation

protocol BottomMenuFunctionEvent
{
    //func exitFunctionHandle()
    
    //func saveFunctionHandle()
    
    //func bottomFuntionHandle(index:Int)
    
    func touchSpaceCloseHandle(index:Int)
    
    //func swapTemplateDirection(index:Int)
}

class DIYViewTemplate:UIView,UIGestureRecognizerDelegate{
    
    //init the delegate 
    var menuFunctionDelegate:BottomMenuFunctionEvent!
    

    override init(frame: CGRect) {
        super.init(frame: frame)
        initBackGoundImage()
        initTemplateImage()
        initslideImage()
        AddGesture()
    }

    required init?(coder aDecoder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
    //self functino and Methods
    func initBackGoundImage()
    {
        
        let imageBackTemplate:UIImageView = UIImageView()
        imageBackTemplate.frame = CGRectMake(0, 64, self.frame.width, self.frame.height)
        imageBackTemplate.image = UIImage(named: "DIYBackImage.png")
        imageBackTemplate.tag = 0
        self.addSubview(imageBackTemplate)
    }
    
    func initTemplateImage()
    {
        let imageTemplate:UIImageView = UIImageView()
        imageTemplate.center = self.center
        imageTemplate.frame  = CGRectMake(self.center.x - 175, self.center.y - 175, 350, 350)
        imageTemplate.image = UIImage(named: "T1.png")
        
        imageTemplate.tag = 1
        self.addSubview(imageTemplate)
    }
    
    func initslideImage()
    {
        let imageSlideView:UIImageView = UIImageView()
        imageSlideView.center = self.center
        imageSlideView.frame = CGRectMake(self.center.x, self.center.y,100, 100)
        imageSlideView.image = UIImage(named: "T2.png")
        imageSlideView.userInteractionEnabled = true
        imageSlideView.tag = 2
        self.addSubview(imageSlideView)
        
    }
    
    func AddGesture()
    {
        
        for LogoImageView in self.subviews{
            
            let recognizerPan:UIPanGestureRecognizer = UIPanGestureRecognizer(target: self,
                action:Selector("handleTap:"))
            recognizerPan.delegate = self
            
            let recognizerPinch:UIPinchGestureRecognizer = UIPinchGestureRecognizer(target: self,
                action:Selector("handlePinch:"))
            recognizerPinch.delegate = self
            
            let recognizerRotate:UIRotationGestureRecognizer = UIRotationGestureRecognizer(target: self,
                action:Selector("handleRotate:"))
            
            if LogoImageView.tag > 1
            {
                print("the LogoImage tag is \(LogoImageView.tag)")
                LogoImageView.addGestureRecognizer(recognizerPan)
                LogoImageView.addGestureRecognizer(recognizerPinch)
                LogoImageView.addGestureRecognizer(recognizerRotate)
            }
        }
    }
    
    //gesture Method
    func handleTap(recognizer: UIPanGestureRecognizer)
    {
            print("the imageView tag is \(recognizer.view?.tag)")
            
            let translation = recognizer.translationInView(self)
            
            recognizer.view!.center = CGPoint(x:recognizer.view!.center.x + translation.x,
                y:recognizer.view!.center.y + translation.y)
            
            recognizer.setTranslation(CGPointZero, inView: self)
            print("the translation is \(translation)")
        
    }
    
    func handlePinch(recognizer: UIPinchGestureRecognizer)
    {
        recognizer.view!.transform = CGAffineTransformScale(recognizer.view!.transform,
            recognizer.scale, recognizer.scale)
        recognizer.scale = 1
    }
    
    func handleRotate(recognizer: UIRotationGestureRecognizer)
    {
        recognizer.view!.transform = CGAffineTransformRotate(recognizer.view!.transform, recognizer.rotation)
        recognizer.rotation = 0
    }
    
    //UIGestureDelegate methods
    func gestureRecognizer(gestureRecognizer: UIGestureRecognizer, shouldRecognizeSimultaneouslyWithGestureRecognizer otherGestureRecognizer: UIGestureRecognizer) -> Bool {
        
        return true
    }
    
    override func touchesBegan(touches: Set<UITouch>, withEvent event: UIEvent?) {
        
         self.menuFunctionDelegate.touchSpaceCloseHandle(1)
    }

}