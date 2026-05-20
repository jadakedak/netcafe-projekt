let today;
let currentWeekMonday;
let month_display = document.getElementById("month-label")

function month_num_to_string(month_index){
    const months = ["January","February","March","April","May","June","July","August","September","October","November","December"]
    return months[month_index - 1]
}
function month_string_to_num(month_string){
    month_index = {
        "January": 1, "February": 2, "March": 3, "April": 4,
        "May": 5, "June": 6, "July": 7, "August": 8,
        "September": 9, "October": 10, "November": 11, "December": 12
    }
    return month_index[month_string]
}

function getWeekMonday(date) {
    const d = new Date(date)
    const day = d.getDay()
    d.setDate(d.getDate() - (day === 0 ? 6 : day - 1))
    d.setHours(0, 0, 0, 0)
    return d
}

function getNextweek(){
    today.setDate(today.getDate() + 7)
    return getCurrentWeekDates(today)
}
function getPreviousweek(){
    today.setDate(today.getDate() - 7)
    return getCurrentWeekDates(today)
}
function getCurrentWeekDates(date) {
    const day = date.getDay()
    const monday = new Date(date)
    monday.setDate(date.getDate() - (day === 0 ? 6 : day - 1))
    monday.setHours(0, 0, 0, 0)

    const dayNames = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    const result = {}
    for (let i = 0; i < 7; i++) {
        const d = new Date(monday)
        d.setDate(monday.getDate() + i)
        result["month"] = month_num_to_string(date.getMonth() + 1)
        result["year"] = d.getFullYear()
        result[dayNames[i]] = { date: d.getDate() }
    }
    return result
}

function getdateday(year, month, date){
    const days = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
    return days[new Date(year, month - 1, date).getDay()]
}

function createComputerSelects(){
    for(let cindex in computers){
        let computer = computers[cindex]
        const option = document.createElement("option")
        option.value = `${computer.id}`
        option.textContent = `Computer ${computer.id}`
        document.getElementById("computer-select").appendChild(option)
    }
}
function renderBookingsForWeek() {
    document.querySelectorAll('.booking-block').forEach(el => el.remove())

    const weekEnd = new Date(currentWeekMonday)
    weekEnd.setDate(weekEnd.getDate() + 7)

    const dayNames = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]

    for (const booking of bookings) {
        const start = new Date(booking.booking_start)
        const end = new Date(booking.booking_end)

        if (start < currentWeekMonday || start >= weekEnd) continue

        const dayName = dayNames[start.getDay()]
        const column = document.getElementById(`col-${dayName}`)
        if (!column) continue

        const startMinutes = start.getHours() * 60 + start.getMinutes()
        const endMinutes = end.getHours() * 60 + end.getMinutes()
        const top = (startMinutes / 60) * 48
        const height = Math.max(((endMinutes - startMinutes) / 60) * 48, 24)

        const block = document.createElement('div')
        block.className = 'booking-block'
        if(userid == booking.userid){
            block.style.border = "1px solid #7c3aed"
            block.style.color = "#a78bfa"
            block.style.background = "#1e1228;"

            block.addEventListener("click", () => {
                document.getElementById("booking-id").textContent = booking.id
                const fmt = d => `${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
                document.getElementById("edit-pc").textContent = `PC ${booking.pc_id}`
                document.getElementById("edit-date").textContent = start.toLocaleDateString("en-GB", { weekday: "long", year: "numeric", month: "long", day: "numeric" })
                document.getElementById("edit-start").textContent = fmt(start)
                document.getElementById("edit-end").textContent = fmt(end)
                document.getElementById("booking-edit-window").classList.add("open")
            })
        }else{
            block.style.border = "1px solid #0e7490"
            block.style.color = "#67e8f9"
            block.style.background = "#082f3f"
        }
        block.style.top = `${top}px`
        block.style.height = `${height}px`
        const fmt = d => `${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
        block.textContent = `PC ${booking.pc_id}  ${fmt(start)} - ${fmt(end)}`
        column.appendChild(block)
    }
}

document.getElementById("new-booking-btn").addEventListener("click", () => {
    document.getElementById("modal").style.display = "block"
})
document.getElementById("cancel-btn").addEventListener("click", () => {
    document.getElementById("modal").style.display = "none"
})

document.getElementById("edit-close-btn").addEventListener("click", () => {
    document.getElementById("booking-edit-window").classList.remove("open")
})
document.getElementById("edit-delete-btn").addEventListener("click", async () => {
    let bookingid = document.getElementById("booking-id").textContent
    const response = await fetch(`/api/bookings/delete/${bookingid}`, {
        method: "DELETE",
        headers: {
            "Content-Type": "application/json"
        }
    })
    const data = await response.json()
    if(!data.success){
        alert(data.message)
        return;
    }
    document.getElementById("booking-edit-window").classList.remove("open")
})

document.getElementById("submit-btn").addEventListener("click", async () => {
    document.getElementById("modal").style.display = "none"

    const selected_computer_id = document.getElementById("computer-select").value
    const booking_date  = document.getElementById("booking-date").value
    const booking_start = document.getElementById("booking-start").value
    const booking_end   = document.getElementById("booking-end").value

    const response = await fetch("/api/bookings/add", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            "computer_id": selected_computer_id,
            "userid": userid,
            "booking_start": `${booking_date}T${booking_start}`,
            "booking_end": `${booking_date}T${booking_end}`
        })
    })
    const data = await response.json()
    if(!data.success){
        alert(data.message)
        return
    }
    renderBookingsForWeek()
})

function updateUI(week_update){
    let now = new Date()
    currentWeekMonday = getWeekMonday(today)

    for(let day in week_update){
        let dm = week_update[day]
        if(day == "year" || day == "month"){
            month_display.textContent = `${week_update["month"]} ${week_update["year"]}`
            continue
        }
        let element = document.getElementById(day)
        if(dm["date"] == now.getDate() && month_string_to_num(week_update["month"]) == now.getMonth() + 1 && week_update["year"] == now.getFullYear()){
            element.style.color = "lightblue"
        }else{
            element.style.color = "#6c7a8e"
        }
        element.textContent = `${day.slice(0, 3)} ${dm["date"]}`
    }

    renderBookingsForWeek()
}

document.getElementById("prev-week").addEventListener("click", () => {
    updateUI(getPreviousweek())
    renderBookingsForWeek()
})
document.getElementById("next-week").addEventListener("click", () => {
    updateUI(getNextweek())
    renderBookingsForWeek()
})

document.addEventListener("DOMContentLoaded", () => {
    today = new Date()
    currentWeekMonday = getWeekMonday(today)
    let currentweek = getCurrentWeekDates(today)
    updateUI(currentweek)
    renderBookingsForWeek()
    createComputerSelects()
})
