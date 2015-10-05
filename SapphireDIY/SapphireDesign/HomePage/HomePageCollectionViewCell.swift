//
//  HomePageCollectionViewCell.swift
//  SapphireDesign
//
//  Created by gxwang on 15/8/29.
//  Copyright (c) 2015年 sapphire. All rights reserved.
//

import Foundation
import UIKit

class HomePageCollectionViewCell : UICollectionViewCell {
    
    @IBOutlet weak var priceLabel: UILabel!
    @IBOutlet weak var praiseNum: UIButton!
    func initView() {
        priceLabel.text = "99"
        self.backgroundColor = UIColor.blueColor()
        self.backgroundView = UIImageView(image: UIImage(named: "1_1.png"))
    }
    
    override func layoutSubviews() {
        if praiseNum != nil && priceLabel != nil {
            praiseNum.frame = CGRectMake(self.frame.width-praiseNum.frame.width-10, 10, praiseNum.frame.width, praiseNum.frame.height)
            priceLabel.frame = CGRectMake(self.frame.width-priceLabel.frame.width-10, self.frame.height-priceLabel.frame.height-10, priceLabel.frame.width, priceLabel.frame.height)
        }
    }
    
    
}