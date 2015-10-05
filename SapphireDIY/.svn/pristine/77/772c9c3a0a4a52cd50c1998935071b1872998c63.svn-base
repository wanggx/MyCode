//
//  HomePageViewController.swift
//  Demo
//
//  Created by gxwang on 15/8/22.
//  Copyright (c) 2015年 gxwang. All rights reserved.
//

import Foundation
import UIKit

class HomePageViewController : UIViewController,UIScrollViewDelegate {

    @IBOutlet weak var categorySegment: UISegmentedControl!
    
    var collectView:HomePageCollectionView!

    @IBOutlet weak var scrollView: UIScrollView!
    override func viewDidLoad() {
        super.viewDidLoad()
        println("viewDidLoad")
        initScrollView()
    }
    
    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
    }
    
    override func viewDidLayoutSubviews() {
        super.viewDidLayoutSubviews()
        
        initScrollView()
        initCollectionView()
    }
    
    func initScrollView() {
        scrollView.delegate = self
        scrollView.backgroundColor = UIColor.whiteColor()
        scrollView.contentSize = CGSize(width: scrollView.bounds.width*2, height: scrollView.bounds.height)
    }
    
    func initCollectionView() {
        collectView = NSBundle.mainBundle().loadNibNamed("HomePageCollectionView", owner: self, options: nil)[0] as! HomePageCollectionView
        
        collectView.frame = CGRectMake(0, 0, scrollView.frame.width, scrollView.frame.height)
        collectView.initColelctionView()
        scrollView.addSubview(collectView)
    }
    
    func scrollViewDidEndDecelerating(scrollView: UIScrollView) {
        
        var index = Int((self.scrollView.contentOffset.x + self.scrollView.frame.width/2) / self.scrollView.frame.width)
        println("index is \(index)")
        var frame = self.scrollView.frame
        frame.origin.x = self.scrollView.frame.width * CGFloat(index)
        self.scrollView.scrollRectToVisible(frame, animated: true)
    }
    
    func scrollViewDidEndDragging(scrollView: UIScrollView, willDecelerate decelerate: Bool) {
        if decelerate == false {
            var index = Int((self.scrollView.contentOffset.x + self.scrollView.frame.width/2) / self.scrollView.frame.width)
            println("信息 index is \(index)")
            var frame = self.scrollView.frame
            frame.origin.x = self.scrollView.frame.width * CGFloat(index)
            self.scrollView.scrollRectToVisible(frame, animated: true)
        }
    }
    
    @IBAction func segContorlValueChanged(sender: AnyObject) {
        
    }
    
    @IBAction func categorySegClicked(sender: AnyObject) {
        
        
    }
}

