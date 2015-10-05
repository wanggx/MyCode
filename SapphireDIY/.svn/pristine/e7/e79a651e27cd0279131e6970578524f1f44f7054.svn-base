//
//  MaterialCollectionView.swift
//  SapphireDesign
//
//  Created by 波 冯 on 15/8/25.
//  Copyright (c) 2015年 sapphire. All rights reserved.
//

import Foundation
import UIKit

class MaterialCollectionView:UICollectionView,UICollectionViewDataSource,UICollectionViewDelegate
{
    
    func initOriginalParam()
    {
        self.delegate   = self
        self.dataSource = self
        self.backgroundColor        = UIColor(red: 0.9, green: 0.9, blue: 0.9, alpha: 1)
        self.userInteractionEnabled = true
        self.alwaysBounceVertical   = true
    }
    
    
    //UICollectionView
    func numberOfSectionsInCollectionView(collectionView: UICollectionView) -> Int {
        
        return 1
    }
    
    func collectionView(collectionView: UICollectionView, numberOfItemsInSection section: Int) -> Int {
        return 63
    }
    
    func collectionView(collectionView: UICollectionView, cellForItemAtIndexPath indexPath: NSIndexPath) -> UICollectionViewCell
    {
        
        let cell = collectionView.dequeueReusableCellWithReuseIdentifier("MaterialCollectionViewCell", forIndexPath: indexPath) as! MaterialCollectionViewCell
        
        let imageString:String = "\(indexPath.row + 1)" + ".png"
        cell.configureBasicInfo(imageString)
        
        return cell
    }
    
}