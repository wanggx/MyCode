//
//  CollectionViewLayout.swift
//  Demo
//
//  Created by gxwang on 15/8/22.
//  Copyright (c) 2015年 gxwang. All rights reserved.
//

import Foundation
import UIKit

class CollectCustomLayout: UICollectionViewLayout {
    
    override func collectionViewContentSize() -> CGSize {
        
        var spaceLen:CGFloat = 5
        var cellWidth:CGFloat = CGFloat(Int((self.collectionView!.frame.width - spaceLen)/2))
        spaceLen = self.collectionView!.frame.width - cellWidth*2
        var cellHeight:CGFloat = CGFloat(Int(cellWidth*1.3))
        var singleHeight:CGFloat = CGFloat(Int(cellWidth*0.35))
        var cellCount = self.collectionView!.numberOfItemsInSection(0) - 2
        var totalHeight:CGFloat = CGFloat((cellCount + 1)/2)*(cellHeight + spaceLen)
        if( cellCount % 2 == 0) {
            totalHeight += singleHeight + spaceLen
        }
        totalHeight += 100
        return CGSizeMake(self.collectionView!.frame.width, totalHeight)
    }
    
    override func layoutAttributesForElementsInRect(rect: CGRect) -> [AnyObject]? {
        
        var attributesArray = [AnyObject]()
        var sectionCount:Int = self.collectionView!.numberOfSections()
        for count in 0..<sectionCount {
            var cellCount = self.collectionView!.numberOfItemsInSection(count)
            for i in 0..<cellCount {
                var indexPath =  NSIndexPath(forItem:i, inSection:count)
                var attributes =  self.layoutAttributesForItemAtIndexPath(indexPath)
                attributesArray.append(attributes)
            }
        }
        return attributesArray
    }
    
    override func layoutAttributesForItemAtIndexPath(indexPath: NSIndexPath) -> UICollectionViewLayoutAttributes! {
        
        var attribute =  UICollectionViewLayoutAttributes(forCellWithIndexPath:indexPath)
        
        var spaceLen:CGFloat = 5
        var cellWidth:CGFloat = CGFloat(Int((self.self.collectionView!.frame.width - spaceLen)/2))
        spaceLen = self.self.collectionView!.frame.width - cellWidth*2
        var cellHeight:CGFloat = CGFloat(Int(cellWidth*1.3))
        var singleHeight:CGFloat = CGFloat(Int(cellWidth*0.35))
        
        println("indexPath.item is \(indexPath.item)")
        if(indexPath.item == 0) {
            attribute.frame = CGRectMake(0, 0, self.collectionView!.frame.width, 100)
        } else if indexPath.item == 1 {
            attribute.frame = CGRectMake(0, 100+spaceLen, cellWidth, singleHeight)
        } else {
            var columnIndex:CGFloat = CGFloat((indexPath.item+1) % 2)
            var rowIndex:CGFloat = CGFloat((indexPath.item-1) / 2)
            println("columnIndex is \(columnIndex)")
            println("rowIndex is \(rowIndex)")
            if(columnIndex == 0) {
                attribute.frame = CGRectMake(0, 100+spaceLen+singleHeight + spaceLen + (cellHeight + spaceLen)*(rowIndex - 1), cellWidth, cellHeight)
            } else if(columnIndex == 1) {
                attribute.frame = CGRectMake(cellWidth + spaceLen, 100+spaceLen+(cellHeight + spaceLen)*rowIndex, cellWidth, cellHeight)
            }
        }
        return attribute
    }
    
}

