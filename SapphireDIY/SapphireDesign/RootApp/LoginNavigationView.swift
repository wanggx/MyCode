//
//  LoginNavigationView.swift
//  SapphireDesign
//
//  Created by gxwang on 15/9/14.
//  Copyright (c) 2015年 sapphire. All rights reserved.
//

import Foundation
import UIKit

class LoginNavigationViewController : UIViewController {

    var scrollView:UIScrollView!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        self.view.backgroundColor = UIColor.redColor()
        log.info("navScrollView")
        initNavigationView()

    }
    
    private func initNavigationView() {
        scrollView = UIScrollView(frame: CGRectMake(0, 0, self.view.bounds.width, self.view.bounds.height))
        scrollView.pagingEnabled = true
        scrollView.contentSize = CGSize(width: self.view.bounds.width*3, height: self.view.bounds.height)
        scrollView.backgroundColor = UIColor.blueColor()
        for var i = 0;i<3;++i {
            let imageView = UIImageView(image: UIImage(named: "1_1.png"))
            imageView.frame = CGRectMake(CGFloat(i)*self.view.bounds.width, 0, self.view.bounds.width, self.view.bounds.height)
            scrollView.addSubview(imageView)
            if i==2 {
                let button:UIButton = UIButton(frame: CGRectMake(self.view.bounds.width*2+self.view.bounds.width/2-50, self.view.bounds.height*7/10, 100, 40))
                button.setTitle("开始体验", forState: UIControlState.Normal)
                scrollView.addSubview(button)
                button.rac_signalForControlEvents(UIControlEvents.TouchUpInside).subscribeNext() {
                    (_) in
                    self.view.removeFromSuperview()
                    NSUserDefaults.standardUserDefaults().setBool(true, forKey: LOGIN_FIRST)
                }
            }
        }
        self.view.addSubview(scrollView)
    }
    
    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
    }
    
}
