//
//  BottomPopViewText.swift
//  SapphireDesign
//
//  Created by 波 冯 on 15/9/15.
//  Copyright (c) 2015年 sapphire. All rights reserved.
//

import UIKit
import Foundation

//protocol InputFieldStateChange
//{
//    func addInputText(name:String, text:String)
//    func changeInputText(name:String, newText:String)
//    func changeFontSize(name:String, isAdd:Bool)
//    func changeFontColor(name:String, color:UIColor)
//    func changeFontFamily(name:String, fontname:String)
//}

class BottomPopViewText: UIViewController,UITextFieldDelegate//,ColorSelectListener
{
    
    var textInput:UITextField!
    var maxInputLength:Int = 20
    //var delegate:InputFieldStateChange!
    var inputName:String = "new"
    
    var colorCurView:UIView!
    
    var labelFontNameFactory:LabelFontNameFactory = LabelFontNameFactory()
    
    var lastSelectButton:UIButton!
    
    func resetViewParam()
    {
        inputName = "new"
        textInput.text = ""
        colorCurView.backgroundColor = UIColor.darkTextColor()
        
        lastSelectButton.selected = false
        lastSelectButton = self.view.viewWithTag(100) as! UIButton
        lastSelectButton.selected = true
    }
    
    func resetEditParam(name:String, text:String, color:UIColor, fontName:String)
    {
        inputName = name
        textInput.text = text
        colorCurView.backgroundColor = color
        
        let curIndex = labelFontNameFactory.getFontIndexByName(fontName)
        lastSelectButton.selected = false
        lastSelectButton = self.view.viewWithTag(100 + curIndex) as! UIButton
        lastSelectButton.selected = true
    }
    
    func initParam()
    {
        
        self.view.backgroundColor = UIColor(red: 0.18, green: 0.18, blue: 0.18, alpha: 0.7)//UIColor(red: 0.58, green: 0, blue: 0.83, alpha: 0.75)
        //self.view.backgroundColor = UIColor(patternImage: UIImage(named: "diypopbackground.jpg")!)
        
        self.view.layer.shadowOpacity = 0.8
        self.view.layer.shadowColor = UIColor.blackColor().CGColor
        self.view.layer.shadowOffset = CGSize(width: 1, height: 1)
        
        self.view.layer.borderWidth = 1
        self.view.layer.borderColor = UIColor(red: 0.18, green: 0.18, blue: 0.18, alpha: 0.99).CGColor
        
        textInput = UITextField(frame: CGRectMake(25, 15, 200, 30))
        textInput.borderStyle = UITextBorderStyle.RoundedRect
        textInput.placeholder = "请输入文字"
        textInput.adjustsFontSizeToFitWidth = true
        textInput.minimumFontSize = 12
        textInput.returnKeyType = .Done
        textInput.delegate = self
        //textInput.becomeFirstResponder()
        textInput.clearButtonMode = UITextFieldViewMode.WhileEditing
        self.view.addSubview(textInput)
        
        let btnAddFontSize = UIButton(frame: CGRectMake(240, 20, 20, 20))
        //btnAddFontSize.setTitle("+", forState: UIControlState.Normal)
        btnAddFontSize.backgroundColor = UIColor.clearColor()
        btnAddFontSize.setImage(UIImage(named: "pluss.png"), forState: UIControlState.Normal)
        btnAddFontSize.setImage(UIImage(named: "plus_hs.png"), forState: UIControlState.Highlighted)
        btnAddFontSize.tag = 1
        btnAddFontSize.addTarget(self, action: Selector("btnClicked:"), forControlEvents: UIControlEvents.TouchUpInside)
        self.view.addSubview(btnAddFontSize)
        
        let btnDelFontSize = UIButton(frame: CGRectMake(265, 20, 20, 20))
        //btnDelFontSize.setTitle("-", forState: UIControlState.Normal)
        btnDelFontSize.backgroundColor = UIColor.clearColor()
        btnDelFontSize.setImage(UIImage(named: "minus.png"), forState: UIControlState.Normal)
        btnDelFontSize.setImage(UIImage(named: "minus_hs.png"), forState: UIControlState.Highlighted)
        //btnDelFontSize.titleLabel?.font = UIFont.systemFontOfSize(20)
        //btnDelFontSize.setTitleColor(UIColor.whiteColor(), forState: UIControlState.Normal)
        //btnDelFontSize.layer.cornerRadius = 5
        btnDelFontSize.tag = 2
        btnDelFontSize.addTarget(self, action: Selector("btnClicked:"), forControlEvents: UIControlEvents.TouchUpInside)
        self.view.addSubview(btnDelFontSize)
        
        let colorBackView = UIButton(frame: CGRectMake(self.view.frame.width - 50, 18, 25, 25))
        colorBackView.backgroundColor = UIColor.whiteColor()
        colorBackView.layer.cornerRadius = 3
        
        colorCurView = UIView(frame: CGRectMake(2, 2, 21, 21))
        colorCurView.backgroundColor = UIColor.darkTextColor()
        colorCurView.layer.cornerRadius = 3
        colorCurView.userInteractionEnabled = false
        colorBackView.addSubview(colorCurView)
        
        self.view.addSubview(colorBackView)
        
//        var colorLineView:ColorLineView = ColorLineView(frame:CGRectMake(25, 60, self.view.frame.width - 50, 7))
//        colorLineView.delegate = self
//        self.view.addSubview(colorLineView)
        
        let scrollView = UIScrollView(frame:CGRectMake(25, 80, self.view.frame.width - 50, 30))
        scrollView.backgroundColor = UIColor.clearColor()
        scrollView.contentSize = CGSizeMake(CGFloat(labelFontNameFactory.getFontCount() * 40), 30)
        self.view.addSubview(scrollView)
        
        for(var i:Int = 0; i < labelFontNameFactory.getFontCount(); i++)
        {
            let btnFont:UIButton = UIButton(frame: CGRectMake(CGFloat(40*i), 0, 40, 30))
            btnFont.setTitle("abc", forState: UIControlState.Normal)
            btnFont.setTitleColor(UIColor.darkTextColor(), forState: UIControlState.Normal)
            btnFont.setTitleColor(UIColor.redColor(), forState: UIControlState.Selected)
            btnFont.selected = false
            btnFont.titleLabel?.font = UIFont(name: labelFontNameFactory.getFontNameByIndex(i), size: 15)
            btnFont.titleLabel?.textAlignment = NSTextAlignment.Center
            btnFont.addTarget(self, action: Selector("fontNameClicked:"), forControlEvents: UIControlEvents.TouchUpInside)
            btnFont.tag = i + 100
            if(i == 0)
            {
                btnFont.selected = true
                lastSelectButton = btnFont
            }
            scrollView.addSubview(btnFont)
        }
    }
    
    func fontNameClicked(sender:UIButton)
    {
        lastSelectButton.selected = false
        sender.selected = true
        lastSelectButton = sender
        
        var selectFontName:String = labelFontNameFactory.getFontNameByIndex(lastSelectButton.tag - 100)
        //self.delegate.changeFontFamily(self.inputName, fontname: selectFontName)
    }
//    
    func textFieldShouldReturn(textField: UITextField) -> Bool {
        
        textInput.resignFirstResponder()
        
//        if(self.delegate != nil)
//        {
//            if(self.inputName == "new")
//            {
//                var uuidObj = CFUUIDCreate(nil)
//                self.inputName = "label_" + (CFUUIDCreateString(nil, uuidObj) as String)
//                self.delegate.addInputText(self.inputName, text: textField.text)
//            }
//            else
//            {
//                self.delegate.changeInputText(self.inputName, newText:textField.text)
//            }
//            
//        }
        
        return true
    }
    
//    func textField(textField: UITextField, shouldChangeCharactersInRange range: NSRange, replacementString string: String) -> Bool {
//        
//        var curLen:Int = textField.text.length - range.length + string.length
//        return (curLen <= maxInputLength)
//    }
    
    func btnClicked(sender:UIButton)
    {
//        if(self.inputName == "new")
//        {
//            return
//        }
//        if(sender.tag == 1)
//        {
//            self.delegate.changeFontSize(self.inputName, isAdd: true)
//        }
//        else if(sender.tag == 2)
//        {
//            self.delegate.changeFontSize(self.inputName, isAdd: false)
//        }
    }
    
    
    func setCurSelect(color: UIColor) {
        
        colorCurView.backgroundColor = color
        
        //self.delegate.changeFontColor(self.inputName, color: color)
    }
    
}

extension String
{
    var length:Int
    {
            return self.characters.count
    }
}
