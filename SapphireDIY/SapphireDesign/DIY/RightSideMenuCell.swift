//
//  RightSideMenuCell.swift
//  SapphireDesign
//
//  Created by 冯 波 on 15/9/7.
//  Copyright (c) 2015年 sapphire. All rights reserved.
//

import UIKit
import Foundation

class RightSideMenuCell: UICollectionViewCell {

    @IBOutlet weak var imageView: UIImageView!
    @IBOutlet weak var labelName: UILabel!
    
    
    func configureInfoCell(imageName:String,labelName:String)
    {
        
        self.backgroundColor = UIColor.whiteColor()
        self.imageView.backgroundColor = UIColor.whiteColor()
        
        self.imageView.image = UIImage(named: imageName)
        self.labelName.text  = labelName

    }
    
}
