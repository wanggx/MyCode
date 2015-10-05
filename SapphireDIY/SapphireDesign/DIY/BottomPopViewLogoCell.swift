//
//  BottomPopViewLogoCell.swift
//  SapphireDesign
//
//  Created by 波 冯 on 15/9/14.
//  Copyright (c) 2015年 sapphire. All rights reserved.
//

import UIKit

class BottomPopViewLogoCell: UICollectionViewCell {
    
    var imagePath:String = ""
    
    @IBOutlet weak var imageView: UIImageView!
    
    func resetView()
    {
        self.backgroundColor = UIColor.clearColor()
        
        self.imageView.image = UIImage(named: imagePath)
    }
    
}
