//
//  HomePageScrollView.swift
//  SapphireDesign
//
//  Created by gxwang on 15/8/25.
//  Copyright (c) 2015年 sapphire. All rights reserved.
//

import Foundation
import UIKit

@objc(pScrollViewDelegate)
protocol pScrollViewDelegate {
    optional func setCurrentIndex(index:Int)
}


class HomePageScrollView : UIScrollView,UIScrollViewDelegate {
    
    weak var pDelegate:pScrollViewDelegate?
    
    func initScrollView() {
        self.delegate = self
        self.backgroundColor = UIColor.whiteColor()
        self.pagingEnabled = true
    }
    
    func scrollViewDidEndDecelerating(scrollView: UIScrollView) {
        let index = Int((self.contentOffset.x + self.frame.width/2) / self.frame.width)
        pDelegate?.setCurrentIndex?(index)
    }
    
    
}
