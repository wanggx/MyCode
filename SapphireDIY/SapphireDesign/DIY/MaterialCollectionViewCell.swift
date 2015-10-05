//
//  MaterialCollectionViewCell.swift
//  SapphireDesign
//
//  Created by 波 冯 on 15/8/25.
//  Copyright (c) 2015年 sapphire. All rights reserved.
//

import Foundation
import UIKit


class MaterialCollectionViewCell:UICollectionViewCell
{
    @IBOutlet weak var MaterialImageView: UIImageView!
    @IBOutlet weak var authorHeaderImageView: UIImageView!
    @IBOutlet weak var authorNameLabel: UILabel!
    @IBOutlet weak var authorNameSapphire: UILabel!
    
    
    func configureBasicInfo(imageName:String)
    {
        self.MaterialImageView.image = UIImage(named: imageName)
        self.authorHeaderImageView.image = UIImage(named: "userheadSmall.png")
        self.authorNameLabel.text = "作者"
        self.authorNameSapphire.text = "Alex"
    }
    
    
    override func layoutSubviews() {
        super.layoutSubviews()
        
        MaterialImageView.layer.borderWidth = 1
        MaterialImageView.layer.borderColor = UIColor.lightGrayColor().CGColor
        
    }

    
}