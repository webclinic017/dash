import { Component, OnInit } from '@angular/core';
import { ses } from '../hero';
import {HttpClient , HttpHeaders, HttpClientModule} from '@angular/common/http';

import { Injectable, OnDestroy } from '@angular/core';
import { Observable, timer, Subscription, Subject } from 'rxjs';

import { switchMap, tap, share, retry, takeUntil } from 'rxjs/operators';

import { HeroService , CurrencyInfo} from '../heroes/hero.service';

type ost = OstInfo[];

interface OstInfo {
  c: string
  t: string
}




@Component({
  selector: 'app-cell',
  templateUrl: './cell.component.html',
  styleUrls: ['./cell.component.css']
})

export class CellComponent implements OnInit {

  postId : any;

  currencyInfo$: Observable<CurrencyInfo[]>;


  a : any;

  b : any;

  tab :any;

  dont_show : string[] = [];

    addPersone(e : string, a : string){

    this.b = {"curr" : e , "tf" : a }

    console.log(this.b);

    this.dont_show.push(this.b)
    console.log(this.dont_show)


    this.http.post<any>('http://127.0.0.1:8050/' , {"curr" : e , "tf" : a }  ).subscribe(data => {
        this.postId = data.aa;
        console.log(this.postId)

    })



    }

  constructor( private service : HeroService , private http: HttpClient  ) {

    this.currencyInfo$ = service.getAllCurrencies();

    this.tab = []

   }

  ngOnInit(): void {
    //this.service.getAllCurrencies().subscribe(todo => console.log(todo));


    //this.currencyInfo$.subscribe((value) => {

     //value.map(r) => (r == 'r') ;

     //})

    console.log(this.tab)

  }


}
