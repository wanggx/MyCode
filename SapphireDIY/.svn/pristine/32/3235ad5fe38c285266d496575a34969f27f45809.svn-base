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
    
    var collectView:HomePageCollectionView {
        get {
            return self.collectionView as! HomePageCollectionView
        }
    }
    
    override func collectionViewContentSize() -> CGSize {
        var totalHeight:CGFloat = 0
        var sectionCount = self.collectView.numberOfSections()
        for i in 0..<sectionCount {
            var sectionHeight = self.getSectionTotalHeight(i)
            totalHeight += sectionHeight
            println("section\(i) height is \(sectionHeight)")
        }
        println("totalHeight is \(totalHeight)")
        return CGSizeMake(self.collectView.frame.width, totalHeight)
    }
    
    override func layoutAttributesForElementsInRect(rect: CGRect) -> [AnyObject]? {
        
        var attributesArray = [AnyObject]()
        var sectionCount:Int = self.collectionView!.numberOfSections()
        for count in 0..<sectionCount {
            var cellCount = self.collectView.numberOfItemsInSection(count)
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
        
        var index:NSIndexPath = NSIndexPath(forItem: 0, inSection: 1)
        var otherIndex:NSIndexPath = NSIndexPath(forItem: 1, inSection: 1)
        var cellWidth = CGFloat(Int((self.collectView.frame.width-self.collectView.spaceForCell(index))/2))
        var space = self.collectView.frame.width-cellWidth*2
        
        if indexPath.section == 0 {
            attribute.frame = CGRectMake(0, self.getSectionCellStartHeight(indexPath), self.collectView.frame.width, self.collectView.heightForCell(indexPath))
        } else {
            var firstHeight = self.getSectionTotalHeight(0)
            var startHeight = firstHeight + self.getSectionCellStartHeight(indexPath)
            var cellStartWidth = 0
            if indexPath.item % 2 == 0 {
                attribute.frame = CGRectMake(0, startHeight, cellWidth, self.collectView.heightForCell(indexPath))
            } else {
                attribute.frame = CGRectMake(cellWidth+space, startHeight, cellWidth, self.collectView.heightForCell(indexPath))
            }
        }
        return attribute
    }
}

extension CollectCustomLayout {
    
    func getSectionTotalHeight(section:Int)->CGFloat {
        var totalHeight:CGFloat = 0
        if section == 0 {
            var cellCount = self.collectView.numberOfItemsInSection(section)
            for var i=0;i<cellCount;++i {
                var indexPath:NSIndexPath = NSIndexPath(forItem: i, inSection: 0)
                totalHeight += self.collectView.heightForCell(indexPath)
                totalHeight += self.collectView.spaceForCell(indexPath)
            }
            return totalHeight
        } else if section == 1 {
            var index:NSIndexPath = NSIndexPath(forItem: 0, inSection: 1)
            var otherIndex = NSIndexPath(forItem: 1, inSection: 1)
            
            var cellWidth = CGFloat(Int((self.collectView.frame.width-self.collectView.spaceForCell(index))/2))
            var space = self.collectView.frame.width-cellWidth*2
            
            var firstHeight:CGFloat = self.collectView.heightForCell(index) + self.collectView.spaceForCell(index)
            
            var cellCount = self.collectView.numberOfItemsInSection(section)
            if cellCount%2 != 0 {
                totalHeight = firstHeight + (self.collectView.heightForCell(otherIndex) + space)*CGFloat(cellCount/2)
            } else {
                totalHeight = (self.collectView.heightForCell(otherIndex) + space)*CGFloat((cellCount+1)/2)
            }
        }
        return totalHeight
    }
    
    func getSectionCellStartHeight(indexPath:NSIndexPath)->CGFloat {
        var startHeight:CGFloat = 0
        if indexPath.section == 0 {
            for i in 0..<indexPath.item {
                startHeight += self.collectView.heightForCell(indexPath)
                startHeight += self.collectView.spaceForCell(indexPath)
            }
        } else if indexPath.section == 1 {
            var firstIndex:NSIndexPath = NSIndexPath(forItem: 0, inSection:1)
            var otherIndex:NSIndexPath = NSIndexPath(forItem: 1, inSection:1)
            
            var firstHeight:CGFloat = self.collectView.heightForCell(firstIndex) + self.collectView.spaceForCell(firstIndex)
            
            if indexPath.item == 0 {
                return 0.0
            } else {
                if indexPath.item % 2 == 0 {
                    startHeight = firstHeight + CGFloat(indexPath.item/2-1)*(self.collectView.heightForCell(otherIndex)+self.collectView.spaceForCell(otherIndex))
                } else {
                    startHeight = CGFloat(indexPath.item/2)*(self.collectView.heightForCell(otherIndex)+self.collectView.spaceForCell(otherIndex))
                }
            }
        }
        
        return startHeight
    }
}

