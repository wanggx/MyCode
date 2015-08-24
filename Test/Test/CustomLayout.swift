//
//  CustomLayout.swift
//  Test
//
//  Created by gxwang on 15/8/24.
//  Copyright (c) 2015年 gxwang. All rights reserved.
//

import Foundation
import UIKit

class CustomLayout : UICollectionViewLayout {
    
    override func collectionViewContentSize() -> CGSize {
        var totalHeight:CGFloat = 0
        var sectionCount = self.collectionView!.numberOfSections()
        for i in 0..<sectionCount {
            totalHeight += self.getSectionTotalHeight(i)
        }
        println("totalHeight is \(totalHeight)")
        return CGSize(width: self.collectionView!.frame.width, height: totalHeight)
    }
    
    
    override func layoutAttributesForElementsInRect(rect: CGRect) -> [AnyObject]? {
        
        var attributes:[AnyObject] = [AnyObject]()
        
        var sectionCount = self.collectionView!.numberOfSections()
        for i in 0..<sectionCount {
            var cellCount = self.collectionView!.numberOfItemsInSection(i)
            for j in 0..<cellCount {
                var indexPath = NSIndexPath(forItem: j, inSection: i)
                var attr = self.layoutAttributesForItemAtIndexPath(indexPath)
                attributes.append(attr)
            }
        }

        return attributes
    }
    
    func getSectionTotalHeight(section:Int)->CGFloat {
        var totalHeight:CGFloat = 0
        
        var cellCount = self.collectionView!.numberOfItemsInSection(section)
        
        for i in 0..<cellCount {
            var indexPath:NSIndexPath = NSIndexPath(forItem: i, inSection: section)
            totalHeight += self.collectionView!.heightForCell(indexPath)
            totalHeight += self.collectionView!.spaceForCell(indexPath)
        }

        return totalHeight
    }
    
    func getSectionCellStartHeight(indexPath:NSIndexPath)->CGFloat {
        
        var totalHeight:CGFloat = 0
        
        for var i=0;i<indexPath.item;++i {
            var index:NSIndexPath = NSIndexPath(forItem: i, inSection: indexPath.section)
            totalHeight += self.collectionView!.heightForCell(index)
            totalHeight += self.collectionView!.spaceForCell(index)
        }
        
        return totalHeight
    }
    
    override func layoutAttributesForItemAtIndexPath(indexPath: NSIndexPath) -> UICollectionViewLayoutAttributes! {
        var attr = UICollectionViewLayoutAttributes(forCellWithIndexPath: indexPath)
        
        var totalHeight:CGFloat = 0
        
        for var i=0;i<indexPath.section;++i {
            totalHeight += self.getSectionTotalHeight(i)
        }
        
        println("xx totoalHeight is \(totalHeight)")
        
        var startHeight = self.getSectionCellStartHeight(indexPath)
        var cellHeight = self.collectionView!.heightForCell(indexPath)
        
        println("xx startheight is \(startHeight)")
        
        attr.frame = CGRectMake(0, totalHeight+startHeight, self.collectionView!.frame.width, cellHeight)
        
        
        return attr
    }
}

extension UICollectionView {
    func heightForCell(indexPath:NSIndexPath)->CGFloat {
        if indexPath.section == 0 {
            return 50
        } else if indexPath.section == 1 {
            return 108
        } else {
            return 20
        }
    }
    
    func spaceForCell(indexPath:NSIndexPath)->CGFloat {
        return 10
    }
}




