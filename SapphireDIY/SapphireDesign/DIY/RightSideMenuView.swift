//
//  RightSideMenuView.swift
//  SapphireDesign
//
//  Created by 波 冯 on 15/9/7.
//  Copyright (c) 2015年 sapphire. All rights reserved.
//

import UIKit
import Foundation

class RightSideMenuView: UICollectionView,UICollectionViewDelegate,UICollectionViewDataSource {

    
    var templateCollection = ["T1.png","T2.png","T3.png","T4.png","T5.png","T6.png","T7.png","T8.png"]

    
    func setBasicInfo()
    {
        print("this is the sideMeun view basicInfo")
        self.backgroundColor = UIColor(red: 0.18, green: 0.18, blue: 0.18, alpha: 0.83)
        
        self.layer.borderWidth = 1
        self.layer.borderColor = UIColor(red: 0.18, green: 0.18, blue: 0.18, alpha: 0.99).CGColor
        
        self.delegate   = self
        self.dataSource = self
    }
    
   
    
    func numberOfSectionsInCollectionView(collectionView: UICollectionView) -> Int {
        
        return 1
    }
    
    // CollectionView行数
    func collectionView(collectionView: UICollectionView, numberOfItemsInSection section: Int) -> Int {
        
        //return self.dataCollection.count
        return self.templateCollection.count
    }
    
    // 获取单元格
//    func collectionView(collectionView: UICollectionView, cellForItemAtIndexPath indexPath: NSIndexPath) -> UICollectionViewCell {
//        println("configure the cell***********")
//        // storyboard里设计的单元格
//        let identify:String = "rightSideMenuCell"
//        // 获取设计的单元格，不需要再动态添加界面元素
//        let cell     = self.dequeueReusableCellWithReuseIdentifier(identify, forIndexPath: indexPath) as! RightSideMenuCell
//        var dataitem = self.templateCollection[indexPath.item]
//        
//        cell.configureInfoCell(dataitem, labelName: dataitem)
//        
//        return cell
//    }
    
    
    func collectionView(collectionView: UICollectionView, cellForItemAtIndexPath indexPath: NSIndexPath) -> UICollectionViewCell {
        
        let cell = self.dequeueReusableCellWithReuseIdentifier("rightSideMenuCell", forIndexPath: indexPath) as! RightSideMenuCell
        cell.configureInfoCell(self.templateCollection[indexPath.row], labelName:self.templateCollection[indexPath.row] )
        
        return cell
        
    }
    
    func collectionView(collectionView: UICollectionView, didSelectItemAtIndexPath indexPath: NSIndexPath)
    {
        
        print("collectionView indexPath is \(indexPath.row)")
           
    }

    

    
}
