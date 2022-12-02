import whisper
import mysql.connector
from pyannote.audio import Pipeline
from pydub import AudioSegment
from dash import dcc, html
import re


def check(id):
    mydb = mysql.connector.connect(
        host="159.223.207.111",
        user="sql_dev_mavmedia",
        password="acDf7XtRxeibxyJw",
        database="sql_dev_mavmedia"
    )
    mycursor = mydb.cursor()
    sql = "select * from transcript where video = %s"
    val = [id]
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()
    return len(myresult)

def convert_to_wav(id, file, format):
    print("Convirtiendo a wav")
    given_audio = AudioSegment.from_file(file, format=format)
    outfile = "assets/ready/" + id + ".wav"
    given_audio.export(outfile, format="wav")
    return outfile


def millisec(timeStr):
    spl = timeStr.split(":")
    s = (int)((int(spl[0]) * 60 * 60 + int(spl[1]) * 60 + float(spl[2])) * 1000)
    return s


def do_diarization(file):
    print("Realizando diarizacion")
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization",
                                        use_auth_token="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")
    diarization = pipeline(file)
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        print(f"start={turn.start:.1f}s stop={turn.end:.1f}s speaker_{speaker}")
    with open("diarization.txt", "w") as text_file:
        text_file.write(str(diarization))


def do_grouping():
    print("Realizando agrupamiento")
    dzs = open('diarization.txt').read().splitlines()
    groups = []
    g = []
    lastend = 0

    for d in dzs:
        if g and (g[0].split()[-1] != d.split()[-1]):  # same speaker
            groups.append(g)
            g = []

        g.append(d)

        end = re.findall('[0-9]+:[0-9]+:[0-9]+\.[0-9]+', string=d)[1]
        end = millisec(end)
        if (lastend > end):
            groups.append(g)
            g = []
        else:
            lastend = end
    if g:
        groups.append(g)
    print(*groups, sep='\n')
    return groups


def do_split(id, groups):
    ofile = 'assets/ready/' + id + '.wav'
    print("Realizando spit de audios")
    audio = AudioSegment.from_wav(ofile)
    gidx = -1
    positions = []
    timestamps = []
    for g in groups:
        start = re.findall('[0-9]+:[0-9]+:[0-9]+\.[0-9]+', string=g[0])[0]
        end = re.findall('[0-9]+:[0-9]+:[0-9]+\.[0-9]+', string=g[-1])[1]
        timestamps.append(f"{start}->{end}: ")
        speaker = re.findall('SPEAKER_\d+', string=g[0])[0]
        positions.append(speaker)
        start = millisec(start)  # - spacermilli
        end = millisec(end)  # - spacermilli
        gidx += 1
        file = 'assets/ready/' + id + '_' + str(gidx) + '.wav'

        audio[start:end].export(file, format='wav')
    return gidx, positions, timestamps


def do_transcribe(id, gidx, speakers, times):
    print("Realizando transcripcion")
    tfinal = []
    inputs = []
    model = whisper.load_model("base")
    uniS = set(speakers)
    unicos = list(uniS)
    # print(f"Se han encontrado {len(unicos)} speakers")
    for item in unicos:
        # print(f"Nuevo nombre para {item}")
        inputs.append(dcc.Input(
            placeholder=f"New name for: {item}",
            type='text',
            value='',
            id=item,
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
        ))
        # newName = input()
        # speakers = list(map(lambda x: x.replace(item, newName), speakers))
        # unicos = list(map(lambda x: x.replace(item, newName), unicos))
    for i in range(gidx + 1):
        file = 'assets/ready/' + id + '_' + str(i) + '.wav'
        result = model.transcribe(file)
        message = speakers[i] + ": " + result["text"]
        insert_db(id, speakers[i], result["text"], times[i])
        tfinal.append(html.P(message))
    tfinal.append(html.Div(
        id="divfinal",
        children=inputs
    ))
    return html.Div(tfinal)


def insert_db(id, speaker, message, tiempo):
    mydb = mysql.connector.connect(
        host="159.223.207.111",
        user="sql_dev_mavmedia",
        password="acDf7XtRxeibxyJw",
        database="sql_dev_mavmedia"
    )

    mycursor = mydb.cursor()
    sql = "INSERT INTO transcript (video, speaker,message, time) VALUES (%s, %s,%s, %s)"
    val = (id, speaker, message, tiempo)
    mycursor.execute(sql, val)
    mydb.commit()
    print(mycursor.rowcount, "record inserted.")


def update_db(id, speaker, remplazo):
    mydb = mysql.connector.connect(
        host="159.223.207.111",
        user="sql_dev_mavmedia",
        password="acDf7XtRxeibxyJw",
        database="sql_dev_mavmedia"
    )

    mycursor = mydb.cursor()
    sql = "update transcript set speaker = %s where speaker = %s and video = %s"
    val = (remplazo, speaker, id)
    mycursor.execute(sql, val)
    mydb.commit()
    print(mycursor.rowcount, "record updated.")


def transfer(id):
    mydb = mysql.connector.connect(
        host="159.223.207.111",
        user="sql_dev_mavmedia",
        password="acDf7XtRxeibxyJw",
        database="sql_dev_mavmedia"
    )
    mycursor = mydb.cursor()
    sql = "select * from transcript where video = %s"
    val = [id]
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()
    f = open("final.txt", "w")
    for x in myresult:
        f.write(x[4])
        f.write(f"[{x[2]}] ")
        f.write(x[3])
        f.write("\n")
        f.close()
