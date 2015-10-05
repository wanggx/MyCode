//
//  TextFieldEffects.swift
//  SapphireDesign
//
//  Created by 冯 波 on 15/8/21.
//  Copyright (c) 2015年 sapphire. All rights reserved.
//

import Foundation
import UIKit

protocol TextFieldsEffectsProtocol {
    func drawViewsForRect(rect: CGRect)
    func updateViewsForBoundsChange(bounds: CGRect)
    func animateViewsForTextEntry()
    func animateViewsForTextDisplay()
}

public class TextFieldEffects : UITextField, TextFieldsEffectsProtocol {
    
    let placeholderLabel = UILabel()
    
    func animateViewsForTextEntry() {
        fatalError("\(__FUNCTION__) must be overridden")
    }
    
    func animateViewsForTextDisplay() {
        fatalError("\(__FUNCTION__) must be overridden")
    }
    
    func drawViewsForRect(rect: CGRect) {
        fatalError("\(__FUNCTION__) must be overridden")
    }
    
    func updateViewsForBoundsChange(bounds: CGRect) {
        fatalError("\(__FUNCTION__) must be overridden")
    }
    
    override public func prepareForInterfaceBuilder() {
        drawViewsForRect(frame)
    }
    
    // MARK: - Initializers
    
    //    public override init() {
    //        super.init()
    //    }
    
    public override init(frame: CGRect) {
        super.init(frame: frame)
    }
    
    required public init(coder aDecoder: NSCoder) {
        super.init(coder: aDecoder)
    }
    
    override public func awakeFromNib() {
        super.awakeFromNib()
    }
    
    // MARK: - Overrides
    
    override public func drawRect(rect: CGRect) {
        drawViewsForRect(rect)
    }
    
    override public func drawPlaceholderInRect(rect: CGRect) {
        // Don't draw any placeholders
    }
    
    // MARK: - UITextField Observing
    
    override public func willMoveToSuperview(newSuperview: UIView!) {
        if newSuperview != nil {
            NSNotificationCenter.defaultCenter().addObserver(self, selector: "textFieldDidEndEditing", name:UITextFieldTextDidEndEditingNotification, object: self)
            
            NSNotificationCenter.defaultCenter().addObserver(self, selector: "textFieldDidBeginEditing", name:UITextFieldTextDidBeginEditingNotification, object: self)
        } else {
            NSNotificationCenter.defaultCenter().removeObserver(self)
        }
    }
    
    public func textFieldDidBeginEditing() {
        animateViewsForTextEntry()
    }
    
    public func textFieldDidEndEditing() {
        animateViewsForTextDisplay()
    }
    
}

