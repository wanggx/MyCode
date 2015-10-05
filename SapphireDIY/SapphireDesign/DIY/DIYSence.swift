//
//  DIYSence.swift
//  SapphireDesign
//
//  Created by 波 冯 on 15/9/8.
//  Copyright (c) 2015年 sapphire. All rights reserved.
//

import Foundation
import SpriteKit
import UIKit

class DIYScene:SKScene,UIGestureRecognizerDelegate{

    var selectNode:SKNode!
    var backgroundNode = SKSpriteNode(imageNamed: "DIYBackImage.png")
    var isSingleTouched:Bool = false
    var isMultiTouched:Bool  = false
    
    //add the gesture methods
    var xStartScale:CGFloat = 0.15
    var yStartScale:CGFloat = 0.15
    
    
    override func didMoveToView(view: SKView) {
        
        self.backgroundColor = UIColor.whiteColor()
        addBackGroundChild()
        addTshirtChild()
        addMaterialChild()
        addGestureMethods()
        
    }
    
    override func touchesBegan(touches: Set<UITouch>, withEvent event: UIEvent?) {
    
        if(touches.count == 1)
        {
            let locationInNode:CGPoint = (touches.first as UITouch!).locationInNode(self)

            let node = self.nodeAtPoint(locationInNode)
          
            if(node.name != "backGroundImage" )
            {
                isSingleTouched = true
                isMultiTouched  = false
                print("The node name is \(node.name)")
                selectNode = node
            }
        }else if(touches.count == 2)
        {
            isMultiTouched = true
            isSingleTouched = false
            let locationInNode:CGPoint = (touches.first as UITouch!).locationInNode(self)
            let node = self.nodeAtPoint(locationInNode)
            print("the multiTouch node name is \(node.name)")
            selectNode = node
        }
        
    }
    
    override func touchesEnded(touches: Set<UITouch>, withEvent event: UIEvent?) {
    
        isSingleTouched = false
        isMultiTouched  = false
    }
    
    override func touchesMoved(touches: Set<UITouch>, withEvent event: UIEvent?) {
        
        
        var location = (touches.first as UITouch!).locationInNode(self)
        print("the location is \(location)")
        if(isSingleTouched == true)
        {
            print("the self location is \(self.position)")
            //tshirt.position = CGPoint(x:location.x, y:location.y)
            selectNode.position = CGPoint(x:location.x, y:location.y)
            
        }
        
    }
    
    func addGestureMethods()
    {
        let pinchTouch = UIPinchGestureRecognizer(target: self, action: Selector("pinchtouch:"))
        self.view?.addGestureRecognizer(pinchTouch)
    }
    
    func addBackGroundChild()
    {
       
        //var backgroundNode       = SKSpriteNode(imageNamed: "DIYBackImage.png")
        backgroundNode.position  = CGPoint(x:CGRectGetMidX(self.frame), y:CGRectGetMidY(self.frame))
        backgroundNode.zPosition = 0
        backgroundNode.name = "backGroundImage"
        //backgroundNode.setScale(0.3)
        self.addChild(backgroundNode)
    }
    
    func  addTshirtChild()
    {
        let tshirt       = SKSpriteNode(imageNamed: "T1.png")
        tshirt.position = CGPoint(x:CGRectGetMidX(self.frame), y:CGRectGetMidY(self.frame))
        tshirt.zPosition = 0.5
        tshirt.name = "fengbo"
        tshirt.setScale(0.45)
        self.addChild(tshirt)
    }
    
    func addMaterialChild()
    {
        let M1 = SKSpriteNode(imageNamed: "vertical.png")
        M1.position = CGPoint(x:CGRectGetMidX(self.frame), y:CGRectGetMidY(self.frame))
        M1.zPosition = 0.6
        M1.name = "vertical1"
        M1.setScale(0.3)
        self.addChild(M1)
        
        let M4 = SKSpriteNode(imageNamed: "vertical.png")
        M4.position = CGPoint(x:CGRectGetMidX(self.frame), y:CGRectGetMidY(self.frame))
        M4.zPosition = 0.6
        M4.name = "vertical2"
        M4.setScale(0.3)
        self.addChild(M4)
        
        let M2 = SKSpriteNode(imageNamed: "Horizontal.png")
        M2.position = CGPoint(x:CGRectGetMidX(self.frame), y:CGRectGetMidY(self.frame))
        M2.zPosition = 0.6
        M2.name = "Horizontal1"
        M2.setScale(0.3)
        self.addChild(M2)
        
        let M3 = SKSpriteNode(imageNamed: "Horizontal.png")
        M3.position = CGPoint(x:CGRectGetMidX(self.frame), y:CGRectGetMidY(self.frame))
        M3.zPosition = 0.6
        M3.setScale(0.3)
        M3.name = "Horizontal2"
        self.addChild(M3)
    }
    
    //gesture methods
    func pinchtouch(sender:UIPinchGestureRecognizer)
    {
//        recognizer.view!.transform = CGAffineTransformScale(recognizer.view!.transform,
//        recognizer.scale, recognizer.scale)
        
        //sender.view?.transform = CGAffineTransformScale(sender.view!.transform,sender.scale, sender.scale)
       
        
        print("the pintouch methods has been intriggerd")
        if (isMultiTouched == true)
        {
            selectNode.xScale = xStartScale*sender.scale
            selectNode.yScale = yStartScale*sender.scale
        }
        if(sender.state == UIGestureRecognizerState.Ended)
        {
            isSingleTouched = false
            isMultiTouched  = false
        }

    }
    
    func gestureRecognizer(_: UIGestureRecognizer,
        shouldRecognizeSimultaneouslyWithGestureRecognizer:UIGestureRecognizer) -> Bool {
            return true
    }
    
}
