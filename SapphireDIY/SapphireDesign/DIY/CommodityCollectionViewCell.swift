//
//  CommodityCollectionViewCell.swift
//  SapphireDesign
//
//  Created by 波 冯 on 15/8/25.
//  Copyright (c) 2015年 sapphire. All rights reserved.
//

import Foundation
import UIKit


class CommodityCollectionViewCell:UICollectionViewCell
{
    
    @IBOutlet weak var CommodityImage: UIImageView!
    @IBOutlet weak var userHeadImage: UIImageView!
    @IBOutlet weak var userNameLabel: UILabel!
    @IBOutlet weak var commodityPriceLabel: UILabel!
    
    
    
    func configureCommodityBasicInfo(imageName:String)
    {
        CommodityImage.image = UIImage(named: imageName)
        userNameLabel.text = "Alex"
        commodityPriceLabel.text = "价格：79"
        userHeadImage.image = UIImage(named: "userheadSmall.png")
    }
    
    override func layoutSubviews() {
        super.layoutSubviews()
        
        CommodityImage.layer.borderWidth = 1
        CommodityImage.layer.borderColor = UIColor.lightGrayColor().CGColor
        
    }
    
}