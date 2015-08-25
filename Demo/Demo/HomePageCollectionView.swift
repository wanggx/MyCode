//
//  HomePageCollectionView.swift
//  Demo
//
//  Created by gxwang on 15/8/24.
//  Copyright (c) 2015年 gxwang. All rights reserved.
//

import Foundation
import UIKit

@objc(pHomeCollectionView)
protocol pHomeCollectionView {
    optional func heightForCell(indexPath:NSIndexPath)->CGFloat
    optional func spaceForCell(indexPath:NSIndexPath)->CGFloat
}


class HomePageCollectionView : UICollectionView ,UICollectionViewDelegate,UICollectionViewDataSource, pHomeCollectionView
{
    
    func initColelctionView() {
        self.backgroundColor = UIColor.clearColor()
        self.dataSource = self
        self.delegate = self
        self.registerClass(UICollectionViewCell.self, forCellWithReuseIdentifier: "cell")
    }
    
    func numberOfSectionsInCollectionView(collectionView: UICollectionView) -> Int {
        return 2
    }
    
    func collectionView(collectionView: UICollectionView, numberOfItemsInSection section: Int) -> Int {
        if section == 0 {
            return 1
        } else if section == 1 {
            return 7
        }
        return 0
    }
    
    func collectionView(collectionView: UICollectionView, cellForItemAtIndexPath indexPath: NSIndexPath) -> UICollectionViewCell {
        var cell = collectionView.dequeueReusableCellWithReuseIdentifier("cell", forIndexPath: indexPath) as! UICollectionViewCell
        
        cell.backgroundView = UIImageView(image: UIImage(named: "1_1.png"))
        cell.backgroundColor = UIColor.blueColor()
        
        return cell
    }
    
    
    func spaceForCell(indexPath: NSIndexPath) -> CGFloat {
        return 5
    }
    
    
    func heightForCell(indexPath: NSIndexPath) -> CGFloat {
        if indexPath.section == 0 {
            return 80
        } else {
            if indexPath.item == 0 {
                return 70
            }
            return 230
        }
    }
    
}
