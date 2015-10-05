//
//  BottomPopViewLogoLayout.swift
//  SapphireDesign
//
//  Created by 波 冯 on 15/9/14.
//  Copyright (c) 2015年 sapphire. All rights reserved.
//

import Foundation
import UIKit

import UIKit

class BottomPopViewLogoLayout: UICollectionViewLayout {
    
    var radius:CGFloat = 48 + 6
    
    // 内容区域总大小，不是可见区域
    override func collectionViewContentSize() -> CGSize {
        
        let lineCount:Int = Int(self.collectionView!.frame.width/radius)
        let rowCount:Int = Int(collectionView!.numberOfItemsInSection(0)/lineCount) + 1
        
        return CGSizeMake(collectionView!.frame.width, CGFloat(rowCount)*radius + 20)
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
        
        let lineCount:Int = Int(self.collectionView!.frame.width/radius)
        let restLen:CGFloat = self.collectionView!.frame.width - radius*CGFloat(lineCount)
        
        let topStart:CGFloat = 10 + 3
        var leftStart:CGFloat = restLen/2 + 3
        var exLen:CGFloat = 0
        
        while(leftStart > 20)
        {
            leftStart -= CGFloat(lineCount-1)
            exLen += 2
        }
        
        let rowIndex:Int = indexPath.item/lineCount
        let lineIndex:Int = indexPath.item - lineCount*rowIndex
        
        //当前单元格布局属性
        let attribute =  UICollectionViewLayoutAttributes(forCellWithIndexPath:indexPath)
        
        attribute.frame = CGRect(x: leftStart + CGFloat(lineIndex)*(radius+exLen), y: topStart + CGFloat(rowIndex)*radius, width: radius-6, height: radius-6)
        
        return attribute
        
    }
    
}

