//
//  BottomPopViewLogo.swift
//  SapphireDesign
//
//  Created by 冯 波 on 15/9/14.
//  Copyright (c) 2015年 sapphire. All rights reserved.
//

import UIKit
import Foundation

protocol BottomPopViewListener
{
    func selectForLogo(logoName:String)
    func selectForOrnament(ornament:String)
}

class BottomPopViewLogo: UICollectionView,UICollectionViewDataSource,UICollectionViewDelegate {
    
    var dataCollection = ["1.png","2.png","3.png","4.png","5.png","6.png","7.png","8.png","9.png","10.png","11.png","12.png","13.png","14.png","15.png","16.png","17.png","18.png","19.png","20.png"]
    var selectdelegate:BottomPopViewListener!
    
    func initMineParam()
    {
        self.backgroundColor = UIColor(red: 0.18, green: 0.18, blue: 0.18, alpha: 0.7)
        
        self.layer.shadowOpacity = 0.8
        self.layer.shadowColor = UIColor.blackColor().CGColor
        self.layer.shadowOffset = CGSize(width: 1, height: 1)
        self.layer.borderWidth = 1
        self.layer.borderColor = UIColor(red: 0.18, green: 0.18, blue: 0.18, alpha: 0.99).CGColor
        
        self.delegate = self
        self.dataSource = self
    }
    
    override func reloadData() {
        
        self.showsHorizontalScrollIndicator = false
        
        super.reloadData()
    }
    
    override func awakeFromNib() {
        
        super.awakeFromNib()
    }
    
    func numberOfSectionsInCollectionView(collectionView: UICollectionView) -> Int {
        return 1
    }
    
    // CollectionView行数
    func collectionView(collectionView: UICollectionView, numberOfItemsInSection section: Int) -> Int {
        
        return self.dataCollection.count
    }
    
    // 获取单元格
    func collectionView(collectionView: UICollectionView, cellForItemAtIndexPath indexPath: NSIndexPath) -> UICollectionViewCell {
        
        // storyboard里设计的单元格
        let identify:String = "poplogocell"
        // 获取设计的单元格，不需要再动态添加界面元素
        let cell = self.dequeueReusableCellWithReuseIdentifier(identify, forIndexPath: indexPath) as! BottomPopViewLogoCell
        
        cell.imagePath = self.dataCollection[indexPath.item]
        cell.resetView()
        return cell
    }
    
//    func collectionView(collectionView: UICollectionView, didSelectItemAtIndexPath indexPath: NSIndexPath) {
//        
//        self.selectdelegate.selectForLogo(self.dataCollection[indexPath.item])
//        
//    }
    
}



