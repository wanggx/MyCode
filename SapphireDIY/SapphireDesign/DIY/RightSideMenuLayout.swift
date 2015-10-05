//
//  RightSideMenuLayout.swift
//  SapphireDesign
//
//  Created by 波 冯 on 15/9/7.
//  Copyright (c) 2015年 sapphire. All rights reserved.
//

import Foundation
import UIKit


class RightSideMenuLayout:UICollectionViewLayout {
    
    // 内容区域总大小，不是可见区域
    override func collectionViewContentSize() -> CGSize {
        
        return CGSizeMake(90, CGFloat(collectionView!.numberOfItemsInSection(0)) * 110 + 125)
        
    }
    
    // 所有单元格位置属性
    override func layoutAttributesForElementsInRect(rect: CGRect) -> [UICollectionViewLayoutAttributes]? {
        
        var attributesArray = [UICollectionViewLayoutAttributes]()
        
        let cellCount = self.collectionView!.numberOfItemsInSection(0)
        
        for i in 0..<cellCount {
            
            let indexPath =  NSIndexPath(forItem:i, inSection:0)
            
            let attributes =  self.layoutAttributesForItemAtIndexPath(indexPath)
            
            attributesArray.append(attributes)
            
        }
        
        return attributesArray
    }
    
    // 这个方法返回每个单元格的位置和大小
    override func layoutAttributesForItemAtIndexPath(indexPath: NSIndexPath) -> UICollectionViewLayoutAttributes! {
        
        //当前单元格布局属性
        let attribute =  UICollectionViewLayoutAttributes(forCellWithIndexPath:indexPath)
        
        attribute.frame = CGRect(x: 5, y: 10 + 110*indexPath.item, width: 80, height: 100)
        
        return attribute
        
    }
    
    
}