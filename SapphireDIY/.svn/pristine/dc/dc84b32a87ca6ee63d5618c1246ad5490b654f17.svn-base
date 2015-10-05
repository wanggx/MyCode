//
//  MaterialCustomLayout.swift
//  SapphireDesign
//
//  Created by 冯 波 on 15/8/25.
//  Copyright (c) 2015年 sapphire. All rights reserved.
//

import UIKit
import Foundation

class MaterailCustomLayout : UICollectionViewLayout {
    
    override func collectionViewContentSize() -> CGSize {
        
        var spaceLen:CGFloat  = 5
        let cellWidth:CGFloat = CGFloat(Int((self.collectionView!.frame.width - spaceLen)/2))
        spaceLen = self.collectionView!.frame.width - cellWidth*2
        let cellHeight:CGFloat = CGFloat(Int(cellWidth*1.3))
        let cellCount = self.collectionView!.numberOfItemsInSection(0)
        //var totalHeight:CGFloat = CGFloat((cellCount + 1)/2)*(cellHeight + spaceLen)
        
        let totalHeight:CGFloat = CGFloat((cellCount+1)/2)*(cellHeight + spaceLen)
        
//        if(cellCount % 2 == 0)
//        {
//            totalHeight += spaceLen
//        }
        return CGSizeMake(self.collectionView!.frame.width, totalHeight + 160)
    }
    
    override func layoutAttributesForElementsInRect(rect: CGRect) -> [UICollectionViewLayoutAttributes]? {
        
        var attributesArray = [UICollectionViewLayoutAttributes]()
        let cellCount = self.collectionView!.numberOfItemsInSection(0)
        for i in 0..<cellCount {
            
            let indexPath  =  NSIndexPath(forItem:i, inSection:0)
            let attributes =  self.layoutAttributesForItemAtIndexPath(indexPath)
            attributesArray.append(attributes)
        }
        return attributesArray
    }
    
    override func layoutAttributesForItemAtIndexPath(indexPath: NSIndexPath) -> UICollectionViewLayoutAttributes! {
        
        let attribute =  UICollectionViewLayoutAttributes(forCellWithIndexPath:indexPath)
        
        var spaceLen:CGFloat = 5
        let cellWidth:CGFloat = CGFloat(Int((self.collectionView!.frame.width - spaceLen)/2))
        spaceLen = self.collectionView!.frame.width - cellWidth*2
        let cellHeight:CGFloat = CGFloat(Int(cellWidth*1.3))
        
        let columnIndex:CGFloat = CGFloat(indexPath.item % 2) //区分是第一列还是第二列
        let rowIndex:CGFloat = CGFloat(indexPath.item / 2)
            
        if(columnIndex == 0)
        {
            //attribute.frame = CGRectMake(0, (cellHeight + spaceLen)*(rowIndex - 1), cellWidth, cellHeight)
            attribute.frame = CGRectMake(0, (cellHeight + spaceLen)*rowIndex, cellWidth, cellHeight)
        }
        else if(columnIndex == 1)
        {
            attribute.frame = CGRectMake(cellWidth + spaceLen, (cellHeight + spaceLen)*rowIndex, cellWidth, cellHeight)
            //attribute.frame = CGRectMake(cellWidth + spaceLen, (cellHeight + spaceLen)*rowIndex, cellWidth, cellHeight)
        }
        
        
        return attribute
    }
    
}



