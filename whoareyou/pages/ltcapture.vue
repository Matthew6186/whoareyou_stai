<template>
    <div>
      <h1>（確認用）LTキャプチャー</h1>
      <v-container>
        <v-row>
          <v-col cols="4">
            撮影日を選択してください <br>
            <v-date-picker
              v-model="inputDate"
              locale="ja-JP"
              :events=arrayEvents
              event-color="green lighten-1"
              :day-format="date => new Date(date).getDate()"
            ></v-date-picker>
            
          </v-col>
          <v-col cols="8">
            撮影時刻を選択してください <br>
            <v-time-picker
              ref="inputTime"
              v-model="inputTime"
              format="24hr"
              use-seconds
            ></v-time-picker>
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="3">
            <v-btn @click="asyncData(inputDate, inputTime)">
                LTを取得
              </v-btn>
          </v-col>
          <v-col cols="9">
            <v-card>
              {{ errMessage }}
            </v-card>
          </v-col>
        </v-row>
        <v-row>
          <v-col>
            <v-card>
              <v-img
              :src = "image"
              max-width="1200"
              position="left"
              ></v-img>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </div>
  </template>
  
  <script lang="ts">
  import { indexedAccessType } from '@babel/types'
  import {
      defineComponent,
      reactive,
      useContext,
      onMounted,
    } from '@nuxtjs/composition-api'

  import format from '@nuxtjs/date-fns'
import { fileURLToPath } from 'url'
  
  type Image = {
    // index: number,
    src: string,
    // category: string
  }

  type State = {
    images: Image[]
  }

  // const generateImgPath = (fileName: string): string => {
  //   return new URL(`../assets/${fileName}`, import.meta.url).href
  // }

  export default defineComponent({
    data() {
      return {
        inputDate: "2023-3-19",
        inputTime: "11:50:00",
        errMessage: "",
        arrayEvents: [""],
        imagepath: "",
        fname: "20230315_084311348793.png",
        img1 : "",
        img2 : ""
      }
    },
    props: {
      label: {
        type: String,
        default: "日付",
        required: false,
      },
      date: {
        type: String,
        default: null,
        required: true,
      },
    },
    mounted () {
      this.arrayEvents = [...Array(2)].map(() => {
        const d = new Date(2023,2,20)
        return d.toISOString().substr(0, 10)
      })
    },
    setup() {
      const headers = [
        { text: 'インデックス', value: 'index' },
        { text: 'ファイルパス', value: 'src' },
        { text: 'タグ', value: 'category' },
      ]
      const Gallery = {
        data() {
          return {
            images: [
              {
                index: 1,
                src: "static/20230315_084311348793.png",
                category: "test1"
              },
              {
                index: 2,
                src: "static/20230315_084747432500.png",
                category: "test2"
              },
            ]
            };
          },
        };
      const state = reactive<State>({
        images: [],
      })
      const { $axios } = useContext()
      onMounted(() => {
        // getZennArticles()
      })
      return { headers, state }
    },
    methods: {
      async asyncData(captureDate:string, captureTime:string) {
        // this.img1 = require("@/assets/20230315_084311348793.png")
        // this.img2 = require("@/assets/20230315_084747432500.png")

        const url = 'http://localhost:8000/ltcapture/'
        const parsedDate = this.$dateFns.parse(captureDate, "yyyy-MM-dd", new Date())
        const parsedTime = this.$dateFns.parse(captureTime, "HH:mm:ss", new Date())
        const params = {
          yr:parsedDate.getFullYear(),
          mt:parsedDate.getMonth()+1,
          dy:parsedDate.getDate(),
          hr:parsedTime.getHours(),
          mi:parsedTime.getMinutes(),
          se:parsedTime.getSeconds(),
        }
        const response = await this.$axios.$get<Image[]>(url, { params }).catch(err => {
          return err.response
        })

        console.log(response)
        console.log(response.fname)
        console.log(response.content)

        this.errMessage = response.content
        this.fname = response.fname
        const filename = "../static/ltcaps/" + response.fname
        // const filename = "../assets/" + "20230315_084311348793.png"
        console.log(filename)
        // const fname = 
        this.imagepath = filename
        // this.imagepath = require(filename)
        // this.imagepath = require("@/assets/" + "20230315_084311348793.png")
        // this.imagepath = require("@/assets/" +  response.fname)
        // this.imagepath = this.generateImgPath(response.fname)
        // this.fname = response.fname
      }
    },
    computed: {
      image: function() :NodeRequire{
        return require('@/assets/ltcaps/' + this.fname)
      }
    }
  })
  </script>