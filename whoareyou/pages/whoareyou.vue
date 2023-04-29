<template>
  <v-form>
    <h1>S耐 Who Are You ?</h1>

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
          カーナンバーを入力してください <br>
          <v-text-field
            v-model="inputCarNum"
            placeholder="Input Car Number"
            inputmode="numeric"
          ></v-text-field>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="3">
          <v-btn @click="asyncData(inputCarNum,inputDate,inputTime)">
            検索を開始
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
          <v-data-table
            :headers="headers"
            :items="state.results"
            dense
            hide-default-footer
          >
          </v-data-table>
        </v-col>
      </v-row>
    </v-container>
  </v-form>

</template>



<script lang="ts">
  import {
    defineComponent,
    reactive,
    useContext,
    onMounted,
  } from '@nuxtjs/composition-api'

  type Driver = {
    carNo: number
    Class: string
    MachineName: string
    DriverCategory: string
    DriverName: string
  }

  type State = {
    results: Driver[]
  }

  export default defineComponent({
    data() {
      return {
        inputCarNum: 0,
        inputDate: "2023-3-19",
        inputTime: "11:50:00",
        errMessage: "",
        arrayEvents: [""]
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
        { text: 'carNo', value: 'carNo'},
        { text: 'Class', value: 'class'},
        { text: 'MachineName', value: 'carname'},
        { text: 'DriverCategory', value: 'drivercategory'},
        { text: 'DriverName', value: 'drivername' },
      ]
      const state = reactive<State>({
        results: [],
      })
      const { $axios } = useContext()
      // const getStaiDriver = async () => {
        // const url = 'http://localhost:8000/data/850?yr=2023&mt=03&dy=19&hr=14&mi=34&se=20'
        // const url = 'http://localhost:8000/data/'
        // const carNo = 850
        // const params = {
        //   yr:2023,
        //   mt:3,
        //   dy:19,
        //   hr:14,
        //   mi:34,
        //   se:20
        // }
        // const response = await $axios.$get<Driver[]>(url+carNo, { params }).catch(err => {
        //   return err.response
        // })
        // state.results = response
      // }
      onMounted(() => {
        // getStaiDriver()
      })
      return { headers, state }
    },
    methods: {
      async asyncData(carNumber: number,captureDate:string, captureTime:string){
        const url = 'http://localhost:8000/data/'
        const carNo = carNumber
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
        const response = await this.$axios.$get<Driver[]>(url+carNo, { params }).catch(err => {
          return err.response
        })

        console.log(response)
        console.log(response.content)

        this.errMessage = response.content
        this.state.results = [response]

      },
    }
  })
</script>