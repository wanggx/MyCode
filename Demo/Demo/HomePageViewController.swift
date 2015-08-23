//
//  HomePageViewController.swift
//  Demo
//
//  Created by gxwang on 15/8/22.
//  Copyright (c) 2015年 gxwang. All rights reserved.
//

import Foundation
import UIKit

class HomePageViewController : UIViewController,UICollectionViewDataSource,UICollectionViewDelegate {

    @IBOutlet weak var categorySegment: UISegmentedControl!
    @IBOutlet weak var collectionView: UICollectionView!
    
    
    override func viewDidLoad() {
        super.viewDidLoad()
        println("viewDidLoad")
        collectionView.backgroundColor = UIColor.clearColor()

    }
    
    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
    }
    
    @IBAction func segContorlValueChanged(sender: AnyObject) {
        
        var segControl:UISegmentedControl = sender as! UISegmentedControl
        if segControl.selectedSegmentIndex == 0 {
            println("0")
        } else {
            println("1")
        }
    }
    
    @IBAction func categorySegClicked(sender: AnyObject) {
        
        
    }
    
    func numberOfSectionsInCollectionView(collectionView: UICollectionView) -> Int {
        return 2

    }
    
    func collectionView(collectionView: UICollectionView, numberOfItemsInSection section: Int) -> Int {
        if section == 0 {
            return 1
        }
        return 9
    }
    
    func collectionView(collectionView: UICollectionView, cellForItemAtIndexPath indexPath: NSIndexPath) -> UICollectionViewCell {
        var cell = collectionView.dequeueReusableCellWithReuseIdentifier("cell", forIndexPath: indexPath) as! UICollectionViewCell
        cell.backgroundColor = UIColor.blueColor()
        
        cell.backgroundView = UIImageView(image: UIImage(named: "1_1.png"))
        
        return cell
    }
    
    func collectionView(collectionView: UICollectionView, didSelectItemAtIndexPath indexPath: NSIndexPath) {
        
    }
    
}

