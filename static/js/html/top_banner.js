document.write(`
<div id="top_banner">
    <div class="title">
        THMSS - Facilities & Rooms Booking System
    </div>
    <div class="logout">
        <a href="logout">Logout</a>
    </div>
</div>
<div id="top_banner2">
    <table>
        <tr>
            <td>
                <a href="/home"> Home </a>
            </td>
            <td>
                <a href="/booking"> Booking </a>
            </td>
            <td style="display: { ["initial", "none"][permission["ADDRECORD"]] |safe }">
                <a href="/records"> My Records </a>
            </td>
        </tr>
    </table>
</div>
`);
